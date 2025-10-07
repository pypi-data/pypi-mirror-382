Wanting
#######

Wanting is a library for creating, and working with models that can represent
incomplete information.

Motivation
**********

Instances of domain models don't always spring into existence fully formed.
They may be partially constructed intially, then filled in over time. Making a
model field optional that is not intially available, but eventually required is
inaccurate because an optional field may *always* be optional, so it never has
to be filled in. It would be better to make the field a required union of the
type it wants, and a placholder type. The wanting types are such placeholders.
They can include metadata, such as the source of the update with missing data,
and even partial data from that source.

Usage
*****

A domain model may look like this:

.. code-block:: python

    from typing import Literal

    import pydantic
    import wanting


    class User(pydantic.BaseModel):
        """A model that can have incomplete information."""

        name: str
        employee_id: str | wanting.Unavailable
        department_code: Literal["TECH", "FO", "BO", "HR"] | wanting.Unmapped
       
Then there is an onboarding system that creates a ``User``. However, the
``employee_id`` is unavailable at this time because it will be generated later.
The onboarding system sources the department code from some other system, which
uses different values than those in the ``User`` model. The onboarding system
knows how to map some of the codes from the other system to the ``User``
department codes, but not all of them. However, because ``employee_id``, and
``department_code`` may also be wanting fields in the ``User`` model, the
onboarding system can still create a fully valid model, while also indicating
that some information is missing:

.. code-block:: python

    user = User(
        name="Charlotte",
        employee_id=wanting.Unavailable(source="onboarding"),
        department_code=wanting.Unmapped(source="onboarding", value="art"),
    )

The model validates, and all the wanting fields serialize to valid JSON:

.. code-block:: python

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

This user can now be persisted, then queried, and updated later by other
systems.

A model class can be queried for its potentially wanting fields:

.. code-block:: python

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

A model instance can be queried for its wanting values:

.. code-block:: python

    p = Parent(
        non_wanting=1,
        wanting=2,
        nested=Child(non_wanting=3, wanting=wanting.Unavailable(source="doc")),
    )
    assert wanting.wanting_values(p) == {
        "nested": {"wanting": wanting.Unavailable(source="doc")}
    }

A model instance can also be serialized, either including or excluding its
wanting values:

.. code-block:: python

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

Model serialization with respect to wanting fields is invertible. A model can
be serialized, then the result can be deserialized back into an equivalent
model.

.. code-block:: python

    p2 = Parent.model_validate(p.model_dump())
    assert p == p2
