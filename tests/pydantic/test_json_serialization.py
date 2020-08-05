import decimal
import typing

import pytest

from fhirzeug.generators.python_pydantic.templates.resource_header import (
    FHIRAbstractBase,
    _without_empty_items,
)


class ExampleModel(FHIRAbstractBase):
    """A Test class to check JSON serialization."""

    decimal: typing.Optional[decimal.Decimal]


@pytest.mark.parametrize(
    "input,expected",
    [
        ("12", '{"decimal": 12}'),
        (12, '{"decimal": 12}'),
        ("12.0", '{"decimal": 12.0}'),
        (12.0, '{"decimal": 12.0}'),
        (1230000, '{"decimal": 1230000}'),
        ("0.00001", '{"decimal": 0.00001}'),
        (decimal.Decimal("12.000"), '{"decimal": 12.000}'),
        (None, "{}"),
    ],
)
def test_decimal_serialization(input, expected):
    model = ExampleModel(decimal=input)
    serialized = model.json()
    assert serialized == expected

    if input:
        assert str(ExampleModel.parse_raw(serialized).decimal) == str(input)


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ([], None),
        ([None], None),
        ({"empty": None}, None),
        ([{"empty": None}], None),
        ([{"empty": [], "example": "example"}], [{"example": "example"}]),
    ],
)
def test_without_empty_items(input: typing.Any, expected: typing.Any):
    assert _without_empty_items(input) == expected
