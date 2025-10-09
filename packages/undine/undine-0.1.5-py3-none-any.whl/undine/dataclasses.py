from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from graphql import Undefined

from undine.typing import TModel

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import UnionType

    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.db.models import Model, OrderBy, Q, QuerySet
    from graphql import FieldNode, InlineFragmentNode

    from undine import QueryType
    from undine.relay import PaginationHandler
    from undine.typing import (
        DispatchProtocol,
        DjangoExpression,
        LiteralArg,
        QuerySetMap,
        RelatedField,
        RelationType,
        TypeHint,
    )

__all__ = [
    "AbstractSelections",
    "BulkCreateKwargs",
    "FilterResults",
    "GraphQLHttpParams",
    "LazyGenericForeignKey",
    "LazyLambda",
    "LazyRelation",
    "LookupRef",
    "MaybeManyOrNonNull",
    "OptimizationWithPagination",
    "OrderResults",
    "Parameter",
    "RelInfo",
    "RootAndInfoParams",
    "TypeRef",
    "UnionFilterRef",
]


@dataclasses.dataclass(frozen=True, slots=True)
class Parameter:
    """Represents a parameter for a function."""

    name: str
    annotation: type | UnionType
    default_value: Any = Undefined


@dataclasses.dataclass(frozen=True, slots=True)
class FilterResults:
    """Holds the results of a QueryType filtering operation."""

    filters: list[Q]
    aliases: dict[str, DjangoExpression]
    distinct: bool
    none: bool = False
    filter_count: int = 0


@dataclasses.dataclass(frozen=True, slots=True)
class OrderResults:
    """Holds the results of a QueryType ordering operation."""

    order_by: list[OrderBy]
    aliases: dict[str, DjangoExpression]
    order_count: int = 0


@dataclasses.dataclass(frozen=True, slots=True)
class GraphQLHttpParams:
    """Holds the parameters from a GraphQL HTTP request."""

    document: str
    variables: dict[str, Any]
    operation_name: str | None
    extensions: dict[str, Any]


@dataclasses.dataclass(frozen=True, slots=True)
class TypeRef:
    """A reference to a type used by converters."""

    value: TypeHint

    total: bool = True
    """If the type hint is in a TypedDict, whether the TypedDict has totality of not."""


@dataclasses.dataclass(frozen=True, slots=True)
class MaybeManyOrNonNull:
    """A reference to a maybe null or many type used by converters."""

    value: Any
    many: bool
    nullable: bool


@dataclasses.dataclass(frozen=True, slots=True)
class LookupRef:
    """A reference to a lookup expression used by converters."""

    ref: Any
    lookup: str


@dataclasses.dataclass(frozen=True, slots=True)
class UnionFilterRef:
    """
    A string reference that references a model field
    that exists in all models of a FilterSet used for a UnionType.
    """

    ref: str
    models: tuple[type[Model], ...]


@dataclasses.dataclass(frozen=True, slots=True)
class ValidatedPaginationArgs:
    """Pagination arguments that have been validated."""

    after: int | None
    before: int | None
    first: int | None
    last: int | None


@dataclasses.dataclass(slots=True)
class OptimizationWithPagination(Generic[TModel]):
    """Pagination arguments that have been validated."""

    queryset: QuerySet[TModel]
    pagination: PaginationHandler


@dataclasses.dataclass(slots=True)
class QuerySetMapWithPagination(Generic[TModel]):
    """Pagination arguments that have been validated."""

    queryset_map: QuerySetMap
    pagination: PaginationHandler


@dataclasses.dataclass(frozen=True, slots=True)
class RootAndInfoParams:
    root_param: str | None
    info_param: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class LazyRelation:
    """Represents a lazily evaluated field for a related field."""

    field: RelatedField

    def get_type(self) -> type[QueryType]:
        from undine.query import QUERY_TYPE_REGISTRY  # noqa: PLC0415

        return QUERY_TYPE_REGISTRY[self.field.related_model]  # type: ignore[index]


@dataclasses.dataclass(frozen=True, slots=True)
class LazyGenericForeignKey:
    """Represents a lazily evaluated Field for a generic foreign key."""

    field: GenericForeignKey

    def get_types(self) -> list[type[QueryType]]:
        from undine.query import QUERY_TYPE_REGISTRY  # noqa: PLC0415
        from undine.utils.model_utils import generic_relations_for_generic_foreign_key  # noqa: PLC0415

        return [
            QUERY_TYPE_REGISTRY[field.remote_field.related_model]  # type: ignore[index]
            for field in generic_relations_for_generic_foreign_key(self.field)
            if field.remote_field.related_model in QUERY_TYPE_REGISTRY  # type: ignore[index]
        ]


@dataclasses.dataclass(frozen=True, slots=True)
class LazyLambda:
    """Represents a lazily evaluated object behind a lambda function."""

    callback: Callable[[], type[QueryType]]


@dataclasses.dataclass(frozen=True, slots=True)
class RelInfo:
    """Holds information about a related field on a model."""

    relation_type: RelationType

    # Relation source
    field_name: str
    model: type[Model]
    model_pk_type: type
    nullable: bool

    # Relation target
    related_name: str | None  # Null for generic foreign keys
    related_model: type[Model] | None  # Null for generic foreign keys
    related_model_pk_type: type
    related_nullable: bool


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class BulkCreateKwargs(Mapping[str, Any]):
    """Arguments to use in bulk create."""

    update_fields: set[str] | None = dataclasses.field(default=None)

    update_conflicts: bool = dataclasses.field(init=False, default=False)
    unique_fields: set[str] | None = dataclasses.field(init=False, default=None)

    def __post_init__(self) -> None:
        if self.update_fields:
            object.__setattr__(self, "update_conflicts", True)
            object.__setattr__(self, "unique_fields", {"pk"})

    def __iter__(self) -> Iterator[str]:
        return iter(dataclasses.asdict(self))

    def __len__(self) -> int:
        return len(dataclasses.asdict(self))

    def __getitem__(self, key: str) -> Any:
        return dataclasses.asdict(self)[key]

    def __bool__(self) -> bool:
        return self.update_conflicts and bool(self.update_fields) and bool(self.unique_fields)


T = TypeVar("T")


@dataclasses.dataclass(frozen=True, slots=True)
class DispatchImplementations(Generic[T]):
    """Holds the implementations of a `FunctionDispatcher`."""

    types: dict[type, DispatchProtocol[T]] = dataclasses.field(default_factory=dict)
    instances: dict[object, DispatchProtocol[T]] = dataclasses.field(default_factory=dict)
    literals: dict[LiteralArg, DispatchProtocol[T]] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(slots=True)
class AbstractSelections:
    """Flattened selections for an abstract type."""

    field_nodes: list[FieldNode] = dataclasses.field(default_factory=list)
    inline_fragments: list[InlineFragmentNode] = dataclasses.field(default_factory=list)
