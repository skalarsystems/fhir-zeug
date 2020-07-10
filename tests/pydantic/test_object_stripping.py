import pytest
import typing

from pydantic import ValidationError

from fhirzeug.generators.python_pydantic.templates.fhir_basic_types import FHIRString
from fhirzeug.generators.python_pydantic.templates.resource_header import (
    FHIRAbstractBase,
)


class ChildModel(FHIRAbstractBase):
    child_field_a: typing.Optional[FHIRString]


class RootModel(FHIRAbstractBase):
    field_a: ChildModel


@pytest.mark.parametrize(
    "subject_reference",
    [{"child_field_a": ""}, {"child_field_a": " "}, {"child_field_a": None}],
)
def test_skipped_resource(subject_reference):

    with pytest.raises(ValidationError):
        RootModel(**{"field_a": subject_reference})
