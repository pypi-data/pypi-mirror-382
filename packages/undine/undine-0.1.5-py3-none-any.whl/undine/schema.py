from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from graphql import (
    DirectiveLocation,
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLScalarType,
    GraphQLSchema,
    GraphQLUnionType,
    validate_schema,
)

from undine.exceptions import UndineErrorGroup
from undine.settings import undine_settings
from undine.utils.graphql.type_registry import get_registered_directives
from undine.utils.graphql.utils import check_directives
from undine.utils.logging import logger
from undine.utils.reflection import get_signature

if TYPE_CHECKING:
    from graphql import GraphQLNamedType

    from undine import RootType
    from undine.directives import Directive

__all__ = [
    "create_schema",
]


def create_schema(
    *,
    query: type[RootType],
    mutation: type[RootType] | None = None,
    subscription: type[RootType] | None = None,
    description: str | None = None,
    schema_definition_directives: list[Directive] | None = None,
    extensions: dict[str, Any] | None = None,
) -> GraphQLSchema:
    """
    Creates the GraphQL schema.

    :param query: The `RootType` for the `Query` operations.
    :param mutation: The `RootType` for the `Mutation` operations.
    :param subscription: The `RootType` for the `Subscription` operations.
    :param description: The description for the schema.
    :param schema_definition_directives: The directives to add to the schema definition.
    :param extensions: The extensions for the schema.
    """
    started = time.perf_counter()
    extensions = extensions or {}

    if schema_definition_directives is not None:
        check_directives(schema_definition_directives, location=DirectiveLocation.SCHEMA)
        extensions[undine_settings.SCHEMA_DIRECTIVES_EXTENSIONS_KEY] = schema_definition_directives

    directives = get_registered_directives()

    logger.debug("Creating Query type...")
    query_object_type: GraphQLObjectType = query.__output_type__()

    mutation_object_type: GraphQLObjectType | None = None
    if mutation is not None:
        logger.debug("Creating Mutation type...")
        mutation_object_type = mutation.__output_type__()

    subscription_object_type: GraphQLObjectType | None = None
    if subscription is not None:
        logger.debug("Creating Subscription type...")
        subscription_object_type = subscription.__output_type__()

    logger.debug("Creating GraphQL schema...")

    schema = GraphQLSchema(
        query=query_object_type,
        mutation=mutation_object_type,
        subscription=subscription_object_type,
        directives=directives,
        description=description,
        extensions=extensions,
    )

    sort_schema_types(schema)

    logger.debug("Validating GraphQL schema...")

    schema_validation_errors = validate_schema(schema)
    if schema_validation_errors:
        msg = "Schema validation failed"
        raise UndineErrorGroup(schema_validation_errors, msg=msg)

    elapsed = time.perf_counter() - started
    logger.debug(f"GraphQL schema created successfully in {elapsed}s!")

    # Clear cached signatures for functions to reduce memory usage.
    get_signature.cache.clear()
    return schema


def sort_schema_types(schema: GraphQLSchema) -> None:
    """Sort Schema types by type and name so that browsing GraphiQL is easier."""

    def key_func(item: tuple[str, GraphQLNamedType]) -> tuple[int, str]:
        match item[1]:
            # Put RootTypes at the end.
            case schema.query_type:
                type_order = 8
            case schema.mutation_type:
                type_order = 9
            case schema.subscription_type:
                type_order = 10
            # Sort more generic types first and then more specific types.
            case GraphQLScalarType():
                type_order = 1
            case GraphQLEnumType():
                type_order = 2
            case GraphQLInterfaceType():
                type_order = 3
            case GraphQLUnionType():
                type_order = 4
            case GraphQLObjectType():
                type_order = 5
            case GraphQLInputObjectType():
                type_order = 6
            case _:
                type_order = 7

        return type_order, item[0]

    schema.type_map = dict(sorted(schema.type_map.items(), key=key_func))
