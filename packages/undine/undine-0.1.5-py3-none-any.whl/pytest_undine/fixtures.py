from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

    from pytest_undine.client import AsyncGraphQLClient, GraphQLClient
    from undine.settings import UndineDefaultSettings

__all__ = [
    "graphql",
    "graphql_async",
    "undine_settings",
]


@pytest.fixture
def graphql() -> GraphQLClient:
    from .client import GraphQLClient  # noqa: PLC0415

    return GraphQLClient()


@pytest.fixture
def graphql_async() -> AsyncGraphQLClient:
    from .client import AsyncGraphQLClient  # noqa: PLC0415

    return AsyncGraphQLClient()


@pytest.fixture
def undine_settings() -> Generator[UndineDefaultSettings, None, None]:
    from undine.settings import undine_settings  # noqa: PLC0415

    try:
        yield undine_settings
    finally:
        undine_settings.reload()  # type: ignore[attr-defined]
