from fhirzeug.fhirspec import FHIRSpec
from fhirzeug.generators.python_pydantic.templates.resource_header import choice_of_validator
from pprint import pprint

import pytest

from pydantic import BaseModel, ValidationError, validator, root_validator
from typing import Optional


# the validator needs to be moved into a pydantic generator section


class X(BaseModel):

    a: Optional[str]
    b: Optional[str]
    c: Optional[str]d

    x: int = 1

    # @validator(*choice_of)
    # def check_only_one(cls, val, values):
    #     if len(values) > 1:
    #         raise ValueError("Only one of the fields is allowed to be set ()")

    _abc_choice_validator = root_validator()(choice_of_validator({"a", "b", "c"}))


@pytest.mark.parametrize(
    "is_ok,data",
    [
        (True, {"a": "Hello"}),
        (True, {"b": "Hello"}),
        (False, {},),
        (False, {"b": "Hello", "c": "World"}),
    ],
)
def test_pydantic_model(is_ok, data):
    """This tests if the function which is used in the template would work"""

    if not is_ok:
        with pytest.raises(ValidationError):
            X(**data)
    else:
        X(**data)


