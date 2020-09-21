"""Test FHIRAbstractBase object."""
import typing

import pydantic
import pytest
from pydantic import ValidationError

from fhirzeug.generators.python_pydantic.templates.resource_header import (
    FHIRAbstractBase,
)


class ExampleModel(FHIRAbstractBase):
    """Simple resource with a boolean field."""

    field_a: bool


class ChildModel(ExampleModel):
    """Child model."""

    pass


class AnotherExampleModel(FHIRAbstractBase):
    """Another resource that has a field of type ChildModel."""

    field_example: ChildModel


def test_unknown_fields_not_allowed():
    with pytest.raises(ValidationError):
        ExampleModel(unknown_field=True)


def test_dynamic_validator():
    """Test dynamic validators with different inheritance use cases."""
    # 1. First case : field_a can take any boolean values in any classes.
    ExampleModel(field_a=True)
    ExampleModel(field_a=False)
    ChildModel(field_a=True)
    ChildModel(field_a=False)
    AnotherExampleModel(field_example={"field_a": True})
    AnotherExampleModel(field_example={"field_a": False})

    # 2. Second case : field_a can only take True values in all classes.
    # Starting from now, field_a value must be True
    ExampleModel._add_post_root_validator(_must_be_true)
    ExampleModel(field_a=True)
    with pytest.raises(pydantic.ValidationError):
        ExampleModel(field_a=False)

    ChildModel(field_a=True)
    with pytest.raises(pydantic.ValidationError):
        ChildModel(field_a=False)

    AnotherExampleModel(field_example={"field_a": True})
    with pytest.raises(pydantic.ValidationError):
        AnotherExampleModel(field_example={"field_a": False})

    # 3. Third use case : field_a has no valid values for class ChildExample
    #    Class AnotherExampleModel is also concerned but not ExampleModel.
    #    Previous rule still apply on all classes.
    ChildModel._add_post_root_validator(_must_be_false)

    ExampleModel(field_a=True)
    with pytest.raises(pydantic.ValidationError):
        ExampleModel(field_a=False)

    with pytest.raises(pydantic.ValidationError):
        ChildModel(field_a=True)
    with pytest.raises(pydantic.ValidationError):
        ChildModel(field_a=False)

    with pytest.raises(pydantic.ValidationError):
        AnotherExampleModel(field_example={"field_a": True})
    with pytest.raises(pydantic.ValidationError):
        AnotherExampleModel(field_example={"field_a": False})


def _must_be_true(values):
    """Root validator to be added to ExampleModel."""
    assert values.get("field_a")
    return values


def _must_be_false(values):
    """Root validator to be added to ChildModel."""
    assert not values.get("field_a")
    return values
