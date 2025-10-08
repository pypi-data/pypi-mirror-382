from __future__ import annotations

from collections import Counter, defaultdict
from contextlib import contextmanager, suppress
from typing import TYPE_CHECKING, Any, TypeGuard

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db import router  # noqa: ICN003
from django.db.models import (
    NOT_PROVIDED,
    CharField,
    F,
    ForeignKey,
    IntegerField,
    ManyToManyField,
    OneToOneField,
    Subquery,
    TextField,
)
from django.db.models.constants import LOOKUP_SEP
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete, pre_save
from django.db.utils import IntegrityError
from django.utils.encoding import force_str

from undine.dataclasses import BulkCreateKwargs
from undine.exceptions import (
    ExpressionMultipleOutputFieldError,
    ExpressionNoOutputFieldError,
    GraphQLDuplicatePrimaryKeysError,
    GraphQLModelConstraintViolationError,
    GraphQLModelNotFoundError,
    GraphQLModelsNotFoundError,
    GraphQLPrimaryKeysMissingError,
    ModelFieldDoesNotExistError,
    ModelFieldNotARelationError,
)
from undine.integrations.modeltranslation import get_translatable_fields, is_translation_field
from undine.settings import undine_settings
from undine.typing import ModelField
from undine.utils.constraints import get_constraint_message

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
    from django.core.exceptions import ValidationError
    from django.db.models import Field, Manager, ManyToManyRel, Model

    from undine.typing import (
        CombinableExpression,
        GenericField,
        ModelField,
        RelatedField,
        TModel,
        ToManyField,
        ToOneField,
    )

__all__ = [
    "SubqueryCount",
    "convert_integrity_errors",
    "determine_output_field",
    "generic_foreign_key_for_generic_relation",
    "generic_relations_for_generic_foreign_key",
    "get_allowed_bulk_create_fields",
    "get_bulk_create_update_fields",
    "get_instance_or_raise",
    "get_instances_or_raise",
    "get_many_to_many_through_field",
    "get_model",
    "get_model_field",
    "get_model_fields_for_graphql",
    "get_pks_from_list_of_dicts",
    "get_related_name",
    "get_save_update_fields",
    "get_validation_error_messages",
    "is_to_many",
    "is_to_one",
    "lookup_to_display_name",
    "set_forward_ids",
]


def get_default_manager(model: type[TModel]) -> Manager[TModel]:
    """Get the default manager for the given model."""
    return model._meta.default_manager  # type: ignore[return-value]


def get_instance_or_raise(*, model: type[TModel], pk: Any) -> TModel:
    """
    Get model instance by the given key with the given primary key.

    :raises GraphQLModelNotFoundError: If an instance for the given primary key does not exists.
    """
    try:
        return get_default_manager(model).get(pk=pk)
    except model.DoesNotExist as error:  # type: ignore[attr-defined]
        raise GraphQLModelNotFoundError(pk=pk, model=model) from error


def get_instances_or_raise(*, model: type[TModel], pks: list[Any]) -> list[TModel]:
    """
    Get model instances by the given primary keys.

    :raises GraphQLModelsNotFoundError: If an instance for any of the given primary keys does not exist.
    """
    instances: list[TModel] = list(get_default_manager(model).filter(pk__in=pks))
    missing = set(pks) - {instance.pk for instance in instances}
    if missing:
        if len(missing) == 1:
            raise GraphQLModelNotFoundError(pk=missing.pop(), model=model)
        raise GraphQLModelsNotFoundError(missing=missing, model=model)
    return instances


def get_pks_from_list_of_dicts(input_data: list[dict[str, Any]]) -> list[Any]:
    """
    Gets primary keys from a list of dicts while validating that each item in list has a pk
    and there are no duplicates. Primary keys are in the same order as in the given list.

    :raises GraphQLPrimaryKeysMissingError: Some items don't have pk.
    :raises GraphQLDuplicatePrimaryKeysError: There are some duplicate primary keys.
    """
    pks = [data["pk"] for data in input_data if "pk" in data]
    if len(pks) != len(input_data):
        raise GraphQLPrimaryKeysMissingError(got=len(pks), expected=len(input_data))

    if len(set(pks)) != len(pks):
        duplicates = [item for item, count in Counter(pks).items() if count > 1]
        raise GraphQLDuplicatePrimaryKeysError(duplicates=duplicates)

    return pks


def generic_relations_for_generic_foreign_key(fk: GenericForeignKey) -> Generator[GenericRelation, None, None]:
    """Get all GenericRelations for the given GenericForeignKey."""
    from django.contrib.contenttypes.fields import GenericRelation  # noqa: PLC0415

    return (field for field in fk.model._meta._relation_tree if isinstance(field, GenericRelation))


def generic_foreign_key_for_generic_relation(relation: GenericRelation) -> GenericForeignKey:
    """Get the GenericForeignKey for the given GenericRelation."""
    from django.contrib.contenttypes.fields import GenericForeignKey  # noqa: PLC0415

    return next(
        field
        for field in relation.related_model._meta.get_fields()  # type: ignore[union-attr]
        if (
            isinstance(field, GenericForeignKey)
            and field.fk_field == relation.object_id_field_name
            and field.ct_field == relation.content_type_field_name
        )
    )


def get_model(*, name: str, app_label: str | None = None) -> type[Model] | None:
    """Get model if it exists in the app. Optionally specify 'app_label' for only look in that app."""
    if app_label is not None:
        try:
            return apps.get_model(app_label, name)
        except LookupError:
            return None

    for app_conf in apps.get_app_configs():
        with suppress(LookupError):
            return app_conf.get_model(name)

    return None


def get_model_field(*, model: type[Model], lookup: str) -> ModelField:
    """
    Gets a model field from the given lookup string.

    :param model: Django model to start finding the field from.
    :param lookup: Lookup string using Django's lookup syntax. E.g. "foo__bar__baz".
    """
    parts = lookup.split(LOOKUP_SEP)
    last = len(parts)
    field: ModelField | None = None

    for part_num, part in enumerate(parts, start=1):
        if part == "pk":
            field = model._meta.pk
        else:
            try:
                field = model._meta.get_field(part)  # type: ignore[assignment]
            except FieldDoesNotExist as error:
                if not part.endswith("_set"):
                    raise ModelFieldDoesNotExistError(field=part, model=model) from error

                # Field might be a reverse many-related field without `related_name`, in which case
                # the `model._meta.fields_map` will store the relation without the "_set" suffix.
                try:
                    field = model._meta.get_field(part.removesuffix("_set"))  # type: ignore[assignment]
                except FieldDoesNotExist as error:
                    raise ModelFieldDoesNotExistError(field=part, model=model) from error

        if part_num == last:
            break

        if not field.is_relation:  # type: ignore[union-attr]
            raise ModelFieldNotARelationError(field=part, model=model)

        model = field.related_model  # type: ignore[union-attr,assignment]

    if field is None:  # pragma: no cover
        raise ModelFieldDoesNotExistError(field=lookup, model=model) from None

    return field


def get_many_to_many_through_field(field: ManyToManyField | ManyToManyRel) -> ForeignKey:
    """
    Get the field on the through model corresponding to the given many to many field.

    Here is a diagram that represents a many-to-many relationship from 'model_1' to 'model_2',
    where 'model_1' has the 'ManyToManyField' to 'model_2'.

    ( model_1 ).<m2m_field> <-- <source>.( through_model ).<target> --> <m2m_rel>.( model_2 )

    For 'model_1.m2m_field', this function returns 'through_model.source'.
    For 'model_2.m2m_rel', this function returns 'through_model.target'.
    """
    if isinstance(field, ManyToManyField):
        return field.remote_field.through._meta.get_field(field.m2m_reverse_field_name())  # type: ignore[union-attr,return-value]
    return field.through._meta.get_field(field.field.m2m_field_name())  # type: ignore[union-attr,return-value]


def get_related_name(related_field: RelatedField | GenericField) -> str:
    """
    Get by which the relation of this field can be used in:

    - Accessing the relation from a model instance: `instance.related_name.all()`
    - Pre-fetching: `qs.select_related("related_name")` or `qs.prefetch_related("related_name")`
    """
    if hasattr(related_field, "accessor_name"):
        return related_field.accessor_name or related_field.name
    if hasattr(related_field, "get_accessor_name"):  # Django < 5.1
        return related_field.get_accessor_name() or related_field.name
    return related_field.name


def get_related_query_name(related_field: RelatedField | GenericField) -> str:
    """
    Name by which the relation of this field can be used in:

    - Query expressions: `qs.filter(query_name__exact=...)`
    """
    if hasattr(related_field, "related_query_name"):
        if callable(related_field.related_query_name):
            return related_field.related_query_name() or related_field.name
        return related_field.related_query_name or related_field.name
    return related_field.name


def get_field_name(related_field: RelatedField | GenericField) -> str:
    """
    Name by which the relation of this field can be used in:

    - Model meta options: `Model._meta.get_fields("query_name")`
    """
    return related_field.name


def get_model_fields_for_graphql(
    model: type[Model],
    *,
    exclude_nonsaveable: bool = False,
) -> Generator[ModelField, None, None]:
    """
    Get all fields from the model that should be included in a GraphQL schema.

    :param model: The model to get fields from.
    :param exclude_nonsaveable: Whether to include non-relational fields that are not editable or not concrete.
    """
    translatable_fields = get_translatable_fields(model)

    include_translatable = undine_settings.MODELTRANSLATION_INCLUDE_TRANSLATABLE
    """Whether to include translatable fields."""

    include_translations = undine_settings.MODELTRANSLATION_INCLUDE_TRANSLATIONS
    """Whether to include translation fields."""

    for model_field in model._meta._get_fields():
        is_relation = bool(getattr(model_field, "is_relation", False))  # Does field reference a relation?
        editable = bool(getattr(model_field, "editable", True))  # Is field value editable by users?
        concrete = bool(getattr(model_field, "concrete", True))  # Does field correspond to a db column?

        if is_relation:
            yield model_field  # type: ignore[misc]
            continue

        if exclude_nonsaveable and (not editable or not concrete):
            continue

        if not include_translatable and model_field.name in translatable_fields:
            continue

        if not include_translations and is_translation_field(model_field):  # type: ignore[arg-type]
            continue

        yield model_field  # type: ignore[misc]


def get_save_update_fields(instance: Model, *fields: str) -> Iterable[str] | None:
    """
    Update fields to use in saving a model instance.

    >>> instance.save(update_fields=get_save_update_fields(instance, *fields))
    """
    # No need to optimize on create.
    if instance.pk is None:
        return None
    unique_fields: set[str] = set(fields) - {"pk", type(instance)._meta.pk.name}
    # Some fields like 'GenericForeignKey' cannot be in the 'update_fields' set.
    # If they are, we cannot optimize the update to only the fields actually updated.
    if unique_fields.issubset(type(instance)._meta._non_pk_concrete_field_names):  # type: ignore[attr-defined]
        return unique_fields or None
    return None


def get_bulk_create_kwargs(model: type[Model], *fields: str) -> BulkCreateKwargs:
    """
    Get arguments to use in 'queryset.bulk_create' for bulk upsert
    where existing instance is determined by its primary key.

    >>> kwargs = get_bulk_create_kwargs(MyModel, *fields)
    >>> MyModel.objects.bulk_create(objs=instances, **kwargs)
    """
    return BulkCreateKwargs(update_fields=get_bulk_create_update_fields(model, *fields))


def get_bulk_create_update_fields(model: type[Model], *fields: str) -> set[str] | None:
    field_map = get_allowed_bulk_create_fields(model=model)
    allowed_fields = {field for field in fields if field in field_map}
    update_fields = set(fields) & allowed_fields  # Remove unallowed fields.
    return update_fields or None


def get_allowed_bulk_create_fields(model: type[Model]) -> dict[str, Field]:
    return {
        field.name: field  # type: ignore[misc]
        for field in model._meta.get_fields()
        if field.concrete and not field.many_to_many and not getattr(field, "primary_key", False)
    }


def is_to_one(field: ModelField | GenericField) -> TypeGuard[ToOneField]:
    is_one_to_one = bool(getattr(field, "one_to_one", False))
    is_many_to_one = bool(getattr(field, "many_to_one", False))
    return is_one_to_one or is_many_to_one


def is_to_many(field: ModelField | GenericField) -> TypeGuard[ToManyField]:
    is_one_to_many = bool(getattr(field, "one_to_many", False))
    is_many_to_many = bool(getattr(field, "many_to_many", False))
    return is_one_to_many or is_many_to_many


def is_generic_foreign_key(field: ModelField | GenericField) -> TypeGuard[GenericForeignKey]:
    is_many_to_one = bool(getattr(field, "many_to_one", False))
    has_content_type_field = hasattr(field, "ct_field")
    has_object_id_field = hasattr(field, "fk_field")
    return is_many_to_one and has_content_type_field and has_object_id_field


def has_default(field: ModelField | GenericField) -> bool:
    has_auto_default = bool(getattr(field, "auto_now", False)) or bool(getattr(field, "auto_now_add", False))
    return has_auto_default or getattr(field, "default", NOT_PROVIDED) is not NOT_PROVIDED


class SubqueryCount(Subquery):
    """
    Count to-many related objects using a subquery.
    Should be used instead of "models.Count" when there might be collisions
    between counted related objects and filter conditions.

    >>> class Foo(Model):
    >>>     number = IntegerField()
    >>>
    >>> class Bar(Model):
    >>>     number = IntegerField()
    >>>     example = ForeignKey(Foo, on_delete=CASCADE, related_name="bars")
    >>>
    >>> foo = Foo.objects.create(number=1)
    >>> Bar.objects.create(example=foo, number=2)
    >>> Bar.objects.create(example=foo, number=2)
    >>>
    >>> foo = (
    >>>     Foo.objects.annotate(count=Count("bars"))
    >>>     .filter(bars__number=2)
    >>>     .first()
    >>> )
    >>> assert foo.count == 2

    This fails and asserts that count is 4. The reason is that Bar objects are
    joined twice: once for the count, and once for the filter. Django does not
    reuse the join, since it is not aware that the join is the same.

    Therefore, do this instead:

    >>> foo = (
    >>>     Foo.objects.annotate(
    >>>         count=SubqueryCount(
    >>>             Bar.objects.filter(example=OuterRef("pk")),
    >>>         ),
    >>>     )
    >>>     .filter(bars__number=2)
    >>>     .first()
    >>> )
    """

    template = "(SELECT COUNT(*) FROM (%(subquery)s) _count)"
    output_field = IntegerField()

    def __repr__(self) -> str:
        try:
            subquery = str(self.query)
        except Exception:  # noqa: BLE001
            subquery = "<subquery>"
        return f"<{self.__class__.__name__}{self.template % {'subquery': subquery}}>"


def determine_output_field(expression: CombinableExpression, *, model: type[Model]) -> None:
    """Determine the `output_field` for the given expression if it doesn't have one."""
    if hasattr(expression, "output_field"):
        return

    possible_output_fields: dict[type[Field], Any] = {}
    for expr in expression.get_source_expressions():
        if hasattr(expr, "output_field"):
            field: Field = expr.output_field
            possible_output_fields[field.__class__] = field.clone()  # type: ignore[attr-defined]
            continue

        if isinstance(expr, F):
            field = get_model_field(model=model, lookup=expr.name)  # type: ignore[assignment]
            possible_output_fields[field.__class__] = field.clone()  # type: ignore[attr-defined]
            continue

    if len(possible_output_fields) == 0:
        raise ExpressionNoOutputFieldError(expr=expression)

    if len(possible_output_fields) > 1:
        raise ExpressionMultipleOutputFieldError(expr=expression, output_fields=list(possible_output_fields))

    expression.output_field = next(iter(possible_output_fields.values()))


def set_forward_ids(instance: Model) -> None:
    """
    Re-set values in related fields for the given instance.

    This prompts their descriptors to update.

    For foreign keys and one-to-one relations, this sets the "_id" value for the field,
    which can be missing if the related instance was set to the field before it was saved.

    For generic foreign keys, this sets the cached content object for the field,
    which would otherwise be missing due to how the GenericForeignKey descriptor works.
    """
    from django.contrib.contenttypes.fields import GenericForeignKey  # noqa: PLC0415

    for field in instance._meta.get_fields():
        if isinstance(field, GenericForeignKey):
            # Note: If the content object was added to the field before it was saved,
            # and is then accessed using the field's descriptor (__get__), this will not work
            # since the content object gets purged from the field cache.
            setattr(instance, field.name, field.get_cached_value(instance, default=None))

        if isinstance(field, ForeignKey | OneToOneField):
            setattr(instance, field.name, getattr(instance, field.name, None))


@contextmanager
def convert_integrity_errors() -> Generator[None, None, None]:
    """Convert IntegrityErrors raised during the context to a GraphQL error."""
    try:
        yield
    except IntegrityError as error:
        msg = get_constraint_message(error.args[0])
        raise GraphQLModelConstraintViolationError(msg) from error


def lookup_to_display_name(lookup: str, field: ModelField) -> str:
    name_conversion_mapping: dict[str, str] = {
        "exact": "",
        "startswith": "starts_with",
        "endswith": "ends_with",
        "isnull": "is_null",
        "isempty": "is_empty",
    }

    # Text fields support case-insensitive lookups, so use those as default lookups instead
    if isinstance(field, CharField | TextField):
        name_conversion_mapping |= {
            "iexact": "",
            "exact": "exact",
            "istartswith": "starts_with",
            "startswith": "starts_with_exact",
            "iendswith": "ends_with",
            "endswith": "ends_with_exact",
            "icontains": "contains",
            "contains": "contains_exact",
        }

    parts: list[str] = []
    for part in lookup.split(LOOKUP_SEP):
        name = name_conversion_mapping.get(part, part)
        if name:
            parts.append(name)

    return "_".join(parts)


def get_validation_error_messages(validation_error: ValidationError) -> dict[str, list[str]]:
    """
    Get dict of error fields to messages inside the given ValidationError.

    >>> get_validation_error_messages(ValidationError("foo"))
    {"": ["foo"]}
    >>> get_validation_error_messages(ValidationError({"foo": "bar"}))
    {"foo": ["bar"]}
    >>> get_validation_error_messages(ValidationError({"foo": ["bar", "baz"]}))
    {"foo": ["bar", "baz"]}
    """
    error_messages: dict[str, list[str]] = defaultdict(list)  # path -> list of messages

    if hasattr(validation_error, "message"):
        message = validation_error.message
        if validation_error.params:
            with suppress(KeyError):  # Allow for mismatching params
                message %= validation_error.params

        error_messages[""].append(force_str(message))
        return error_messages

    if hasattr(validation_error, "error_dict"):
        for field, errors in validation_error.error_dict.items():
            for error in errors:
                sub_messages = get_validation_error_messages(error)
                for path, messages in sub_messages.items():
                    key = f"{field}.{path}" if path else field
                    error_messages[key].extend(messages)

        return error_messages

    for error in validation_error.error_list:
        sub_messages = get_validation_error_messages(error)
        for path, messages in sub_messages.items():
            error_messages[path].extend(messages)

    return error_messages


@contextmanager
def use_save_signals(
    model: type[Model],
    instances: Iterable[Model],
    update_fields: set[str] | None,
) -> Generator[None, None, None]:
    if pre_save.has_listeners(model):
        for instance in instances:
            pre_save.send(
                sender=model,
                instance=instance,
                raw=False,
                using=router.db_for_write(model, instance=instance),
                update_fields=list(update_fields or []),
            )

    yield

    if post_save.has_listeners(model):
        for instance in instances:
            post_save.send(
                sender=model,
                instance=instance,
                created=True,
                update_fields=list(update_fields or []),
                raw=False,
                using=router.db_for_write(model, instance=instance),
            )


@contextmanager
def use_delete_signals(
    model: type[Model],
    instances: Iterable[Model],
) -> Generator[None, None, None]:
    if pre_delete.has_listeners(model):
        for instance in instances:
            pre_delete.send(
                sender=model,
                instance=instance,
                using=router.db_for_write(model, instance=instance),
                origin=instance,
            )

    yield

    if post_delete.has_listeners(model):
        for instance in instances:
            post_delete.send(
                sender=model,
                instance=instance,
                using=router.db_for_write(model, instance=instance),
                origin=instance,
            )


@contextmanager
def use_m2m_remove_signals(
    model: type[Model],
    source_to_removed_target_pks: dict[Model, set[Any]],
    *,
    target_name: str,
    reverse: bool,
) -> Generator[None, None, None]:
    if not m2m_changed.has_listeners(model):
        yield
        return

    target_model = getattr(model, target_name).field.remote_field.model

    for source, pk_set in source_to_removed_target_pks.items():
        m2m_changed.send(
            sender=model,
            action="pre_remove",
            instance=source,
            reverse=reverse,
            model=target_model,
            pk_set=pk_set,
            using=router.db_for_write(model, instance=source),
        )

    yield

    for source, pk_set in source_to_removed_target_pks.items():
        m2m_changed.send(
            sender=model,
            action="post_remove",
            instance=source,
            reverse=reverse,
            model=target_model,
            pk_set=pk_set,
            using=router.db_for_write(model, instance=source),
        )


@contextmanager
def use_m2m_add_signals(
    model: type[Model],
    source_to_added_target_pks: dict[Model, set[Any]],
    *,
    target_name: str,
    reverse: bool,
) -> Generator[None, None, None]:
    if not m2m_changed.has_listeners(model):
        yield
        return

    target_model = getattr(model, target_name).field.remote_field.model

    for source, pk_set in source_to_added_target_pks.items():
        m2m_changed.send(
            sender=model,
            action="pre_add",
            instance=source,
            reverse=reverse,
            model=target_model,
            pk_set=pk_set,
            using=router.db_for_write(model, instance=source),
        )

    yield

    for source, pk_set in source_to_added_target_pks.items():
        m2m_changed.send(
            sender=model,
            action="post_add",
            instance=source,
            reverse=reverse,
            model=target_model,
            pk_set=pk_set,
            using=router.db_for_write(model, instance=source),
        )
