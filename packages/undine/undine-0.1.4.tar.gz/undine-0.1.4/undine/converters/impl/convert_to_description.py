from __future__ import annotations

from contextlib import suppress
from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import F, Model, Q
from graphql import GraphQLNamedType, GraphQLWrappingType

from undine.converters import convert_to_description
from undine.dataclasses import LazyGenericForeignKey, LazyLambda, LazyRelation, TypeRef
from undine.parsers import docstring_parser
from undine.relay import Connection
from undine.typing import CombinableExpression, ModelField
from undine.utils.text import get_docstring


@convert_to_description.register
def _(ref: Any, **kwargs: Any) -> Any:
    docstring = get_docstring(ref)
    return docstring_parser.parse_body(docstring)


@convert_to_description.register
def _(ref: ModelField, **kwargs: Any) -> Any:
    help_text = getattr(ref, "help_text", None) or None
    if help_text is None:
        return None
    return str(help_text)


@convert_to_description.register
def _(_: type[Model], **kwargs: Any) -> Any:
    return None


@convert_to_description.register
def _(_: CombinableExpression | F | Q, **kwargs: Any) -> Any:
    return None


@convert_to_description.register
def _(_: TypeRef, **kwargs: Any) -> Any:
    return None


@convert_to_description.register
def _(_: type[tuple], **kwargs: Any) -> Any:
    # For NamedTuples, don't use the generated docstring.
    return None


@convert_to_description.register
def _(ref: LazyRelation, **kwargs: Any) -> Any:
    return convert_to_description(ref.field)


@convert_to_description.register
def _(ref: LazyGenericForeignKey, **kwargs: Any) -> Any:
    return convert_to_description(ref.field)


@convert_to_description.register
def _(_: LazyLambda, **kwargs: Any) -> Any:
    return None


@convert_to_description.register
def _(_: GraphQLNamedType, **kwargs: Any) -> Any:
    return None


@convert_to_description.register
def _(ref: GraphQLWrappingType, **kwargs: Any) -> Any:
    return convert_to_description(ref.of_type)


@convert_to_description.register
def _(ref: GenericForeignKey, **kwargs: Any) -> Any:  # Required for Django<5.1
    return getattr(ref, "help_text", None) or None


@convert_to_description.register
def _(ref: Connection, **kwargs: Any) -> Any:
    return ref.description


with suppress(ImportError):
    from undine.utils.full_text_search import PostgresFTS

    @convert_to_description.register
    def _(_: PostgresFTS, **kwargs: Any) -> Any:
        return None
