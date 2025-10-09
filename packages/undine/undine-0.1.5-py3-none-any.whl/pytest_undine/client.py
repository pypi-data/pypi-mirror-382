from __future__ import annotations

import json
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import TYPE_CHECKING, Any

import pytest
from django.contrib.auth import get_user_model
from django.test.client import MULTIPART_CONTENT, AsyncClient, Client
from graphql import FormattedExecutionResult

from undine.http.files import extract_files
from undine.persisted_documents.utils import to_document_id
from undine.settings import undine_settings
from undine.typing import WebSocketASGIScope

from .query_logging import capture_database_queries

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from http.cookies import SimpleCookie

    from django.contrib.auth.models import User
    from django.core.files import File
    from graphql import GraphQLFormattedError

    from undine.typing import DjangoTestClientResponseProtocol

    from .query_logging import DBQueryData
    from .websocket import TestWebSocket

with suppress(ImportError):
    from .websocket import TestWebSocket


__all__ = [
    "AsyncGraphQLClient",
    "GraphQLClient",
    "GraphQLClientHTTPResponse",
    "GraphQLClientWebSocketResponse",
]


IS_CHANNELS_INSTALLED: bool = "TestWebSocket" in globals()


class WebSocketMixin:
    """Mixin to support GraphQL over WebSocket requests."""

    cookies: SimpleCookie

    async def over_websocket(
        self,
        document: str,
        *,
        variables: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        operation_name: str | None = None,
        use_persisted_document: bool = False,
        count_queries: bool = False,
    ) -> AsyncGenerator[GraphQLClientWebSocketResponse, None]:
        """
        Send a GraphQL over WebSocket request and yield the execution results.

        :param document: GraphQL document string to send in the request.
        :param variables: GraphQL variables for the document.
        :param headers: Headers for the request.
        :param operation_name: If given document includes multiple operations,
                               this is required to select the operation to execute.
        :param use_persisted_document: Instead of sending the whole document,
                                       convert it to a persisted document ID and send that.
        :param count_queries: If True, count the number of queries executed during the request.
        """
        variables = variables or {}
        body: dict[str, Any] = {}

        if use_persisted_document:
            body["documentId"] = to_document_id(document)
        else:
            body["query"] = document

        if variables:
            body["variables"] = variables
        if operation_name is not None:
            body["operationName"] = operation_name

        websocket = self.websocket()

        if headers is not None:
            websocket.scope["headers"] += [
                (name.encode("ascii"), value.encode("ascii")) for name, value in headers.items()
            ]

        async with websocket:
            await websocket.connection_init()

            with capture_database_queries(enabled=count_queries) as queries:
                initial_result = await websocket.subscribe(body)

            if initial_result["type"] == "error":
                result = FormattedExecutionResult(data=None, errors=initial_result["payload"])
                yield GraphQLClientWebSocketResponse(result=result, database_queries=queries)
                return

            yield GraphQLClientWebSocketResponse(result=initial_result["payload"], database_queries=queries)

            while True:
                with capture_database_queries(enabled=count_queries) as queries:
                    message = await websocket.receive()

                match message["type"]:
                    case "complete":
                        return

                    case "next":
                        yield GraphQLClientWebSocketResponse(result=message["payload"], database_queries=queries)
                        continue

                    case "error":
                        result = FormattedExecutionResult(data=None, errors=message["payload"])
                        yield GraphQLClientWebSocketResponse(result=result, database_queries=queries)
                        return

                    case _:  # pragma: no cover
                        msg = f"Unexpected message type: {message['type']}"
                        raise RuntimeError(msg)

    def websocket(self, **kwargs: Any) -> TestWebSocket:
        """Create a testing websocket."""
        if not IS_CHANNELS_INSTALLED:  # pragma: no cover
            msg = "The `channels` library is not installed. Cannot create websocket."
            raise RuntimeError(msg)

        scope = self._get_default_scope()
        scope.update(kwargs)  # type: ignore[typeddict-item]

        return TestWebSocket(scope=scope)

    def _get_default_scope(self) -> WebSocketASGIScope:
        # From 'django.test.client.AsyncRequestFactory._base_scope'
        cookies = (f"{morsel.key}={morsel.coded_value}".encode("ascii") for morsel in self.cookies.values())
        path = f"/{undine_settings.WEBSOCKET_PATH}"
        return WebSocketASGIScope(  # type: ignore[typeddict-item]
            type="websocket",
            asgi={"version": "3.0"},
            http_version="1.1",
            scheme="ws",
            server=("testserver", 80),
            client=("127.0.0.1", 0),
            root_path="",
            path=path,
            raw_path=path.encode("ascii"),
            query_string=b"",
            headers=[
                (b"cookie", b"; ".join(sorted(cookies))),
                (b"host", b"testserver"),
                (b"connection", b"Upgrade"),
                (b"upgrade", b"websocket"),
                (b"sec-websocket-version", b"13"),
                (b"sec-websocket-key", b"RKr31GF3kXZqsXjVT7s3Mg=="),
                (b"sec-websocket-protocol", b"graphql-transport-ws"),
            ],
            subprotocols=["graphql-transport-ws"],
            state={},
            extensions={"websocket.http.response": {}},
            cookies={k: str(v) for k, v in self.cookies.items()},
            path_remaining="",
            url_route={"args": (), "kwargs": {}},
            #
            # 'user' and 'session' are set in the `WebSocketContextManager` `AuthMiddlewareStack`.
        )  # type: ignore[typeddict-item]


class GraphQLClient(WebSocketMixin, Client):
    """A GraphQL client for testing."""

    def __call__(
        self,
        document: str,
        *,
        variables: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        operation_name: str | None = None,
        use_persisted_document: bool = False,
        count_queries: bool = False,
    ) -> GraphQLClientHTTPResponse:
        """
        Execute a GraphQL operation synchronously.

        :param document: GraphQL document string to send in the request.
        :param variables: GraphQL variables for the document.
        :param headers: Headers for the request.
        :param operation_name: If given document includes multiple operations,
                               this is required to select the operation to execute.
        :param use_persisted_document: Instead of sending the whole document,
                                       convert it to a persisted document ID and send that.
        :param count_queries: If True, count the number of queries executed during the request.
        """
        variables = variables or {}
        body: dict[str, Any] = {}

        if use_persisted_document:
            body["documentId"] = to_document_id(document)
        else:
            body["query"] = document

        if variables:
            body["variables"] = variables
        if operation_name is not None:
            body["operationName"] = operation_name

        files = extract_files(variables)
        data = _create_multipart_data(body, files) if files else body
        content_type = MULTIPART_CONTENT if files else "application/json"

        with capture_database_queries(enabled=count_queries) as results:
            response: DjangoTestClientResponseProtocol = self.post(  # type: ignore[assignment]
                path=f"/{undine_settings.GRAPHQL_PATH}",
                data=data,
                content_type=content_type,
                headers=headers,
            )

        return GraphQLClientHTTPResponse(response, results)

    def login_with_superuser(self, username: str = "admin", **kwargs: Any) -> User:
        """Create a superuser and log in as that user."""
        defaults = {
            "is_staff": True,
            "is_superuser": True,
            "email": "superuser@django.com",
            **kwargs,
        }
        user, _ = get_user_model().objects.get_or_create(username=username, defaults=defaults)
        self.force_login(user)
        return user

    def login_with_regular_user(self, username: str = "user", **kwargs: Any) -> User:
        """Create a regular user and log in as that user."""
        defaults = {
            "is_staff": False,
            "is_superuser": False,
            "email": "user@django.com",
            **kwargs,
        }
        user, _ = get_user_model().objects.get_or_create(username=username, defaults=defaults)
        self.force_login(user)
        return user


class AsyncGraphQLClient(WebSocketMixin, AsyncClient):
    """An async GraphQL client for testing."""

    async def __call__(
        self,
        document: str,
        *,
        variables: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        operation_name: str | None = None,
        use_persisted_document: bool = False,
        count_queries: bool = False,
    ) -> GraphQLClientHTTPResponse:
        """
        Execute a GraphQL operation asynchronously.

        :param document: GraphQL document string to send in the request.
        :param variables: GraphQL variables for the document.
        :param headers: Headers for the request.
        :param operation_name: If given document includes multiple operations,
                               this is required to select the operation to execute.
        :param use_persisted_document: Instead of sending the whole document,
                                       convert it to a persisted document ID and send that.
        :param count_queries: If True, count the number of queries executed during the request.
        """
        variables = variables or {}
        body: dict[str, Any] = {}

        if use_persisted_document:
            body["documentId"] = to_document_id(document)
        else:
            body["query"] = document

        if variables:
            body["variables"] = variables
        if operation_name is not None:
            body["operationName"] = operation_name

        files = extract_files(variables)
        data = _create_multipart_data(body, files) if files else body
        content_type = MULTIPART_CONTENT if files else "application/json"

        with capture_database_queries(enabled=count_queries) as results:
            response: DjangoTestClientResponseProtocol = await self.post(  # type: ignore[assignment]
                path=f"/{undine_settings.GRAPHQL_PATH}",
                data=data,
                content_type=content_type,
                headers=headers,
            )

        return GraphQLClientHTTPResponse(response, results)

    async def login_with_superuser(self, username: str = "admin", **kwargs: Any) -> User:
        """Create a superuser and log in as that user."""
        defaults = {
            "is_staff": True,
            "is_superuser": True,
            "email": "superuser@django.com",
            **kwargs,
        }
        user, _ = await get_user_model().objects.aget_or_create(username=username, defaults=defaults)
        self.force_login(user)
        return user

    async def login_with_regular_user(self, username: str = "user", **kwargs: Any) -> User:
        """Create a regular user and log in as that user."""
        defaults = {
            "is_staff": False,
            "is_superuser": False,
            "email": "user@django.com",
            **kwargs,
        }
        user, _ = await get_user_model().objects.aget_or_create(username=username, defaults=defaults)
        self.force_login(user)
        return user


class BaseGraphQLClientResponse(ABC):
    """Base class for GraphQLClient responses."""

    DB_QUERIES_NOT_ENABLED_MSG = (
        "Database queries have not been captured. "
        "Enable them using the `count_queries` parameter when calling the client."
    )

    def __init__(self, database_queries: DBQueryData) -> None:
        self._database_queries = database_queries

    @property
    @abstractmethod
    def json(self) -> FormattedExecutionResult:
        """Return the JSON content of the response."""

    # Concrete methods

    def __str__(self) -> str:
        return json.dumps(self.json, indent=2, sort_keys=True, default=str)

    def __repr__(self) -> str:
        return repr(self.json)

    def __getitem__(self, item: str) -> Any:
        return self.json[item]  # type: ignore[literal-required]

    def __contains__(self, item: str) -> bool:
        return item in self.json

    @property
    def queries(self) -> list[str]:
        """Return a list of the database queries that were executed."""
        if not self._database_queries.enabled:
            return pytest.fail(self.DB_QUERIES_NOT_ENABLED_MSG)

        return [info.sql for info in self._database_queries.queries]

    @property
    def query_count(self) -> int:
        """Return the number of database queries that were executed."""
        if not self._database_queries.enabled:
            return pytest.fail(self.DB_QUERIES_NOT_ENABLED_MSG)

        return self._database_queries.count

    @property
    def query_log(self) -> str:
        """Return a string representation of the database queries that were executed."""
        if not self._database_queries.enabled:
            return pytest.fail(self.DB_QUERIES_NOT_ENABLED_MSG)

        return self._database_queries.log

    @property
    def data(self) -> dict[str, Any] | None:
        """Return the data from the response content."""
        return self.json["data"]

    @property
    def results(self) -> dict[str, Any] | list[Any] | None:
        """
        Return the results from the first top-level field in the response content.

        >>> self.json
        {"data": {"foo": {"name": "bar"}}}
        >>> self.results
        {"name": "bar"}
        """
        data = self.data or {}
        try:
            return next(iter(data.values()))
        except StopIteration:
            msg = f"No query object not found in response content\nContent: {self.json}"
            return pytest.fail(msg)

    @property
    def edges(self) -> list[dict[str, Any]]:
        """
        Return edges from the first top-level field in the response content.

        >>> self.json
        {"data": {"foo": {"edges": [{"node": {"name": "bar"}}]}}}
        >>> self.edges
        [{"node": {"name": "bar"}}]
        """
        results = self.results
        if not isinstance(results, dict):
            msg = f"Edges not found in response content\nContent: {self.json}"
            return pytest.fail(msg)

        try:
            return results["edges"]
        except (KeyError, TypeError):
            msg = f"Edges not found in response content\nContent: {self.json}"
            return pytest.fail(msg)

    def node(self, index: int) -> dict[str, Any]:
        """
        Return the node at the given index in the response content edges.

        >>> self.json
        {"data": {"foo": {"edges": [{"node": {"name": "bar"}}]}}}
        >>> self.node(0)
        {"name": "bar"}
        """
        try:
            return self.edges[index]["node"]
        except (IndexError, TypeError):
            msg = f"Node {index!r} not found in response content\nContent: {self.json}"
            return pytest.fail(msg)

    @property
    def has_errors(self) -> bool:
        """Are there any errors in the response?"""
        return "errors" in self.json and self.json.get("errors") is not None

    @property
    def errors(self) -> list[GraphQLFormattedError]:
        """
        Return all errors.

        >>> self.json
        {"errors": [{"message": "bar", "path": [...], ...}]}
        >>> self.errors
        [{"message": "bar", "path": [...], ...}]
        """
        try:
            return self.json["errors"]
        except (KeyError, TypeError):
            msg = f"Errors not found in response content\nContent: {self.json}"
            return pytest.fail(msg)

    def error_message(self, selector: int | str) -> str:
        """
        Return the error message from the errors list...

        1) in the given index

        >>> self.json
        {"errors": [{"message": "bar", ...}]}
        >>> self.error_message(0)
        "bar"

        2) in the given path:

        >>> self.json
        {"errors": [{"message": "bar", "path": ["fizz", "buzz", "foo"], ...}]}
        >>> self.error_message("foo")
        "bar"
        """
        if isinstance(selector, int):
            try:
                return self.errors[selector]["message"]
            except (IndexError, KeyError, TypeError):
                msg = f"Errors message not found from index {selector}\nContent: {self.json}"
                return pytest.fail(msg)
        else:
            try:
                return next(error["message"] for error in self.errors if error["path"][-1] == selector)
            except (StopIteration, KeyError, TypeError):
                msg = f"Errors message not found from path {selector!r}\nContent: {self.json}"
                return pytest.fail(msg)

    def assert_query_count(self, count: int) -> None:
        if not self._database_queries.enabled:
            pytest.fail(self.DB_QUERIES_NOT_ENABLED_MSG)

        if self.query_count != count:
            msg = f"Expected {count} queries, got {self.query_count}.\n{self.query_log}"
            pytest.fail(msg)


class GraphQLClientHTTPResponse(BaseGraphQLClientResponse):
    """An HTTP response from the GraphQLClient."""

    def __init__(self, response: DjangoTestClientResponseProtocol, database_queries: DBQueryData) -> None:
        self.response = response
        super().__init__(database_queries=database_queries)

    @property
    def json(self) -> FormattedExecutionResult:
        """Return the JSON content of the response."""
        return self.response.json()  # type: ignore[return-value]

    @property
    def status_code(self) -> int:
        """Return the status code of the response."""
        return self.response.status_code


class GraphQLClientWebSocketResponse(BaseGraphQLClientResponse):
    """A WebSocket response from the GraphQLClient."""

    def __init__(self, result: FormattedExecutionResult, database_queries: DBQueryData) -> None:
        self.result = result
        super().__init__(database_queries=database_queries)

    @property
    def json(self) -> FormattedExecutionResult:
        """Return the JSON content of the response."""
        return self.result


def _create_multipart_data(body: dict[str, Any], files: dict[File, list[str]]) -> dict[str, Any]:
    path_map: dict[str, list[str]] = {}
    files_map: dict[str, File] = {}
    for i, (file, path) in enumerate(files.items()):
        path_map[str(i)] = path
        files_map[str(i)] = file

    return {
        "operations": json.dumps(body),
        "map": json.dumps(path_map),
        **files_map,
    }
