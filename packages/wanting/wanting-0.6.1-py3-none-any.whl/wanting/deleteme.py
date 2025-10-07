"""Testbed for documentation code."""

from typing import Literal

import pydantic

import wanting

# ruff: noqa: S101


class User(pydantic.BaseModel):
    """A model that can have incomplete information."""

    name: str
    employee_id: str | wanting.Unavailable
    department_code: Literal["TECH", "FO", "BO", "HR"] | wanting.Unmapped


user = User(
    name="Charlotte",
    employee_id=wanting.Unavailable(source="onboarding"),
    department_code=wanting.Unmapped(source="onboarding", value="art"),
)

assert user.model_dump() == {
    "name": "Charlotte",
    "employee_id": {
        "kind": "unavailable",
        "source": "onboarding",
        "value": {"serialized": b"null"},
    },
    "department_code": {
        "kind": "unmapped",
        "source": "onboarding",
        "value": {"serialized": b'"art"'},
    },
}


class Child(pydantic.BaseModel):
    """A model that can have incomplete information."""

    non_wanting: int
    wanting: int | wanting.Unavailable


class Parent(pydantic.BaseModel):
    """A model that can have top-level, and nested incomplete information."""

    non_wanting: int
    wanting: int | wanting.Unavailable
    nested: Child


def reduce_path(path: list[wanting.FieldInfoEx]) -> str:
    """Reduce the FieldInfoEx objects that comprise a path to a readable string."""
    return "->".join(f"{fi.cls.__name__}.{fi.name}" for fi in path)


paths = wanting.wanting_fields(Parent)
summary = [reduce_path(path) for path in paths]
assert summary == ["Parent.wanting", "Parent.nested->Child.wanting"]

p = Parent(
    non_wanting=1,
    wanting=2,
    nested=Child(non_wanting=3, wanting=wanting.Unavailable(source="doc")),
)
assert wanting.wanting_values(p) == {
    "nested": {"wanting": wanting.Unavailable(source="doc")}
}

incex = wanting.wanting_incex(p)
assert p.model_dump(include=incex) == {
    "nested": {
        "wanting": {
            "kind": "unavailable",
            "source": "doc",
            "value": {"serialized": b"null"},
        }
    }
}
assert p.model_dump(exclude=incex) == {
    "non_wanting": 1,
    "wanting": 2,
    "nested": {"non_wanting": 3},
}

p2 = Parent.model_validate(p.model_dump())
assert p == p2
