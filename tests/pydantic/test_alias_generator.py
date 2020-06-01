import pytest
import pydantic
from fhirzeug.generators.python_pydantic.templates.resource_header import (
    fhir_alias_generator,
)


def test_special_names():
    assert fhir_alias_generator("class_") == "class"


def test_camel_case():
    assert fhir_alias_generator("this_is_a_test") == "thisIsATest"


class AliasTestModel(pydantic.BaseModel):

    class_: str
    foo_bar: str

    class Config:
        alias_generator = fhir_alias_generator
        allow_population_by_field_name = True


def test_aliases():
    values = {"class": "foo", "fooBar": "bar"}
    x = AliasTestModel(**values)
    assert x.class_ == "foo"
    assert x.foo_bar == "bar"

    assert x.dict(by_alias=True) == values
