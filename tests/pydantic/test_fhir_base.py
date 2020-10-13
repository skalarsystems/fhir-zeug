"""Test FHIRAbstractBase Model."""
import typing

import pytest
from pydantic import ValidationError

from fhirzeug.generators.python_pydantic.templates.resource_header import (
    FHIRAbstractBase,
)


class ItemModel(FHIRAbstractBase):
    field_a: typing.Optional[str]
    field_b: typing.Optional[str]


class ContainerModel(FHIRAbstractBase):
    field_c: ItemModel


def test_unknown_fields_not_allowed():
    """Test unknown fields are not allowed in FHIRAbstractBase models."""
    ItemModel()
    with pytest.raises(ValidationError):
        ItemModel(unknown_field=True)


def test_list_instead_of_dict_must_fail():
    """Test a list must not be validated as a dict in FHIRAbstractBase models."""
    ContainerModel(field_c={"field_a": "123", "field_b": "456"})

    with pytest.raises(ValidationError):
        ContainerModel(fieldC=[{"field_a": "123", "field_b": "456"}])
