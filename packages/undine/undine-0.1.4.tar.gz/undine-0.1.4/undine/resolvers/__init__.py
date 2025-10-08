"""
Contains different types of resolvers for GraphQL operations.
Resolvers must be callables with the following signature:

(root: Root, info: GQLInfo, **kwargs: Any) -> Any
"""

from __future__ import annotations

from .filter import FilterFunctionResolver, FilterModelFieldResolver, FilterQExpressionResolver
from .mutation import (
    BulkCreateResolver,
    BulkDeleteResolver,
    BulkUpdateResolver,
    CreateResolver,
    DeleteResolver,
    UpdateResolver,
)
from .query import (
    ConnectionResolver,
    EntrypointFunctionResolver,
    FieldFunctionResolver,
    GlobalIDResolver,
    InterfaceResolver,
    ModelAttributeResolver,
    ModelGenericForeignKeyResolver,
    ModelManyRelatedFieldResolver,
    ModelSingleRelatedFieldResolver,
    NestedConnectionResolver,
    NestedQueryTypeManyResolver,
    NestedQueryTypeSingleResolver,
    NodeResolver,
    QueryTypeManyResolver,
    QueryTypeSingleResolver,
    UnionTypeResolver,
)
from .subscription import FunctionSubscriptionResolver, SubscriptionValueResolver

__all__ = [
    "BulkCreateResolver",
    "BulkDeleteResolver",
    "BulkUpdateResolver",
    "ConnectionResolver",
    "CreateResolver",
    "DeleteResolver",
    "EntrypointFunctionResolver",
    "EntrypointFunctionResolver",
    "FieldFunctionResolver",
    "FilterFunctionResolver",
    "FilterModelFieldResolver",
    "FilterQExpressionResolver",
    "FunctionSubscriptionResolver",
    "GlobalIDResolver",
    "InterfaceResolver",
    "ModelAttributeResolver",
    "ModelGenericForeignKeyResolver",
    "ModelManyRelatedFieldResolver",
    "ModelSingleRelatedFieldResolver",
    "NestedConnectionResolver",
    "NestedQueryTypeManyResolver",
    "NestedQueryTypeSingleResolver",
    "NodeResolver",
    "QueryTypeManyResolver",
    "QueryTypeSingleResolver",
    "SubscriptionValueResolver",
    "UnionTypeResolver",
    "UpdateResolver",
]
