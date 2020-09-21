"""Test reference custom validator."""
import pytest
import typing

from fhirzeug.generators.python_pydantic.templates.resource_custom_validators import (
    _reference_validator,
)


@pytest.mark.parametrize(
    ("values", "is_valid"),
    [
        ({"reference": "Patient/23", "type": "Patient"}, True),
        ({"reference": "Patient/23", "type": "Device"}, False),
        ({"reference": "http://fhir.example.org/Patient/23", "type": "Patient"}, True),
        ({"reference": "http://fhir.example.org/Patient/23", "type": "Device"}, False),
        ({"reference": "http://fhir.example.org/Patient/23"}, True),
        ({"reference": "https://example.org/foobar"}, True),
        ({"reference": "ftp://ftp-server.com/foobar/example-0.1"}, True),
        ({"reference": "Patient"}, False),
        ({"reference": "foobar/23"}, False),
        ({"reference": "#foobar"}, True),  # Internal fragment reference
        ({"reference": "#foobar/23"}, True),  # Internal fragment reference
    ],
)
def test_reference_validator(values: typing.Dict, is_valid: bool) -> None:
    """Test reference custom validator."""
    if is_valid:
        _reference_validator(values)
    else:
        with pytest.raises(ValueError):
            _reference_validator(values)
