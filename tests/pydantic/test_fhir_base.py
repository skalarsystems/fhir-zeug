import typing

import pytest
from pydantic import ValidationError

from fhirzeug.generators.python_pydantic.templates.resource_header import (
    FHIRAbstractBase,
)


class ExampleModel(FHIRAbstractBase):
    field_a: typing.Optional[bool]


def test_unknown_fields_not_allowed():
    with pytest.raises(ValidationError):
        ExampleModel(unknown_field=True)
