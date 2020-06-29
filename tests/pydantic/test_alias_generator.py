import pydantic
from fhirzeug.generators.python_pydantic.templates.resource_header import (
    camelcase_alias_generator,
)


def test_special_names():
    assert camelcase_alias_generator("class_") == "class"


def test_camel_case():
    assert camelcase_alias_generator("this_is_a_test") == "thisIsATest"


def test_camel_case_foo():
    assert camelcase_alias_generator("f_o_o_bar") == "fOOBar"


class AliasTestModel(pydantic.BaseModel):

    class_: str
    foo_bar: str

    class Config:
        alias_generator = camelcase_alias_generator
        allow_population_by_field_name = True


def test_aliases():
    values = {"class": "foo", "fooBar": "bar"}
    x = AliasTestModel(**values)
    assert x.class_ == "foo"
    assert x.foo_bar == "bar"

    assert x.dict(by_alias=True) == values
