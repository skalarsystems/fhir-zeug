import typing
import pydantic

from fhirzeug.generators.python_pydantic.templates.resource_header import (
    FHIRAbstractBase,
)


# These tests checks if empty items are cleaned as described
# in https://www.hl7.org/fhir/datatypes.html#representations
# TODO: add support for extensions: https://www.hl7.org/fhir/json.html#null


class ChildModel(FHIRAbstractBase):
    child_field_a: typing.Optional[str]
    child_field_b: typing.Optional[int]
    child_field_c: typing.Optional[bool]


class ListItem(FHIRAbstractBase):
    list_field_a: typing.Optional[str]
    list_field_b: typing.Optional[int]
    list_field_c: typing.Optional[bool]


class RootModel(FHIRAbstractBase):
    field_a: typing.Optional[str]
    field_b: typing.Optional[int]
    field_c: typing.Optional[bool]

    child: typing.Optional["ChildModel"]
    list_items: typing.Optional[typing.List["ListItem"]]


def test_returns_none_if_no_fields():
    assert RootModel().dict() == None


def test_not_set_fields_are_ignored():
    assert RootModel(field_a="a", field_b=1).dict() == {"field_a": "a", "field_b": 1}


def test_nulls_are_ignored():
    assert RootModel(field_a="a", field_b=None).dict() == {
        "field_a": "a",
    }


def test_empty_dicts_are_ignored():
    assert RootModel(field_a="a", child={}).dict() == {
        "field_a": "a",
    }
    assert RootModel(
        field_a="a", child=ChildModel(child_field_a=None, child_field_b=None,)
    ).dict() == {"field_a": "a"}


def test_non_empty_dict_fields_are_serialized():
    assert RootModel(
        field_a="a", child=ChildModel(child_field_a="child a", child_field_b=None,)
    ).dict() == {"field_a": "a", "child": {"child_field_a": "child a"}}


def test_empty_lists_are_ignored():
    assert RootModel(field_a="a", list_items=[]).dict() == {
        "field_a": "a",
    }
    assert RootModel(
        field_a="a", list_items=[ListItem(), ListItem(), ListItem(),]
    ).dict() == {"field_a": "a",}


def test_non_empty_list_items_are_serialized():
    assert RootModel(
        field_a="a",
        list_items=[
            ListItem(list_field_a="list item 1 a"),
            ListItem(),
            ListItem(list_field_a="list item 3 a"),
        ],
    ).dict() == {
        "field_a": "a",
        "list_items": [
            {"list_field_a": "list item 1 a"},
            {"list_field_a": "list item 3 a"},
        ],
    }


def test_empty_strings_are_ignored():
    assert RootModel(field_a="", field_c=True).dict() == {"field_c": True}
