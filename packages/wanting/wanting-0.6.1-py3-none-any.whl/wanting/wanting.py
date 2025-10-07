"""The Wanting module."""

import functools
from collections.abc import Iterator, Mapping
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    NamedTuple,
    TypeGuard,
    Union,
    cast,
    get_origin,
)

import pydantic
import pydantic_core


class Json(pydantic.BaseModel):
    """Wrapper for a JSON value."""

    serialized: bytes


def _to_json(value: Any) -> Json:  # noqa: ANN401
    if isinstance(value, Json):
        return value
    try:
        return Json.model_validate(value)
    except pydantic.ValidationError:
        return Json(serialized=pydantic_core.to_json(value))


class Wanting(pydantic.BaseModel):
    """Abstract class that represents an incomplete field value."""

    kind: str
    source: str
    if TYPE_CHECKING:
        value: Any
    else:
        value: Annotated[Json, pydantic.BeforeValidator(_to_json)]


class Unavailable(Wanting):
    """Represents an unavailable field value."""

    kind: Literal["unavailable"] = "unavailable"
    value: Json = pydantic.Field(default_factory=lambda: Json(serialized=b"null"))


class Unmapped(Wanting):
    """Represents an unmapped field value."""

    kind: Literal["unmapped"] = "unmapped"


class FieldInfoEx(NamedTuple):
    """Extended information about a field."""

    cls: type[pydantic.BaseModel]
    name: str
    info: pydantic.fields.FieldInfo


_UNION_TYPES = {UnionType, Union}


def _is_union_type(typ: object) -> TypeGuard[UnionType]:
    return get_origin(typ) in _UNION_TYPES


def _field_wanting_types(fi: pydantic.fields.FieldInfo) -> Iterator[type[Wanting]]:
    typ = fi.annotation
    if _is_union_type(typ):
        for utyp in typ.__args__:
            if issubclass(utyp, Wanting):
                yield utyp
    elif issubclass(cast("type", typ), Wanting):
        yield cast("type[Wanting]", typ)


def _field_has_wanting_type(fi: pydantic.fields.FieldInfo) -> bool:
    return bool(next(_field_wanting_types(fi), False))


def _field_model_types(fi: pydantic.fields.FieldInfo) -> Iterator[type[pydantic.BaseModel]]:
    typ = fi.annotation
    if issubclass(cast("type", typ), pydantic.BaseModel):
        yield cast("type[pydantic.BaseModel]", typ)
    elif _is_union_type(typ):
        for utyp in typ.__args__:
            if issubclass(utyp, pydantic.BaseModel):
                yield utyp


def wanting_fields(
    cls: type[pydantic.BaseModel], *, depth: int = -1
) -> Iterator[list[FieldInfoEx]]:
    """Get the fields in a model class that could be :class:`Wanting`.

    Args:
        cls: The model class to inspect for wanting fields.
        depth: How deeply to check nested models for wanting fields. The depth
            is zero-based, so ``0`` for only top-level fields. ``-1`` for no
            limit.

    Returns:
        An iterator of :class:`FieldInfoEx` lists, where each list describes
        the path to a top-level, or nested wanting field.
    """
    top_level_wanting_field_paths = (
        [FieldInfoEx(cls, name, fi)]
        for name, fi in cls.model_fields.items()
        if _field_has_wanting_type(fi)
    )
    yield from top_level_wanting_field_paths

    if depth == 0:
        return

    top_level_model_fields = [
        (name, fi, list(_field_model_types(fi))) for name, fi in cls.model_fields.items()
    ]
    nested_wanting_field_paths = (
        [FieldInfoEx(cls, name, fi), *path]
        for name, fi, typs in top_level_model_fields
        for typ in typs
        for path in wanting_fields(typ, depth=depth - 1)
    )
    yield from nested_wanting_field_paths


type WantingValues = Mapping[str, Wanting | WantingValues]


def _wanting_values_reducer(acc: WantingValues, curr: tuple[str, object]) -> WantingValues:
    name, value = curr
    if isinstance(value, Wanting):
        return {**acc, name: value}
    if isinstance(value, pydantic.BaseModel):
        nested = wanting_values(value)
        if nested:
            return {**acc, name: nested}
    return acc


def wanting_values(model: pydantic.BaseModel) -> WantingValues:
    """Get the values in a model instance that are :class:`Wanting`.

    Args:
        model: The model instance to inspect for wanting values.

    Returns:
        A dict that mirrors the structure of the model, but only contains the
        fields that have wanting values.
    """
    return functools.reduce(_wanting_values_reducer, model, {})


type IncExMapping = Mapping[str, bool | IncExMapping]
"""A mapping that describes which fields to include, or exclude during serialization.

Values of this type may be used as the ``include`` or ``exclude`` parameter to
:func:`pydantic.BaseModel.model_dump`.
"""


def _exclude_wanting_values_reducer(
    acc: IncExMapping, curr: tuple[str, Wanting | WantingValues]
) -> IncExMapping:
    name, value = curr
    if isinstance(value, Wanting):
        return {**acc, name: True}
    if isinstance(value, Mapping):
        initial: IncExMapping = {}
        return {
            **acc,
            name: functools.reduce(_exclude_wanting_values_reducer, value.items(), initial),
        }
    return acc


def wanting_incex(model: pydantic.BaseModel) -> IncExMapping:
    """Get an :type:`IncExMapping` for the :class:`Wanting` fields in a model instance."""
    wv = wanting_values(model)
    return functools.reduce(_exclude_wanting_values_reducer, wv.items(), {})
