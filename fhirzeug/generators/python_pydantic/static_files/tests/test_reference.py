"""Test Reference element."""
import pytest
import pydantic
import typing

from pydantic_fhir import r4


@pytest.mark.parametrize(
    ("reference", "good_type", "wrong_type"),
    [
        ("Patient/23", "Patient", "Device"),
        ("Group/23", "Group", "Patient"),
        ("http://fhir.example.org/Patient/23", "Patient", "Device"),
        ("https://another-example.org/Group/23", "Group", "Patient"),
    ],
)
def test_resource_type_consistency(
    reference: str, good_type: str, wrong_type: str
) -> None:
    """Test resource types must match within Reference."""
    r4.Reference(reference=reference, type=good_type)
    with pytest.raises(pydantic.ValidationError):
        r4.Reference(reference=reference, type=wrong_type)


def test_absolute_reference_not_url() -> None:
    """Test reference must be a url if not REST format."""
    r4.Reference(reference="http://fhir.example.org/Patient/23")
    r4.Reference(reference="https://example.org/foobar")
    r4.Reference(reference="ftp://ftp-server.com/foobar/example-0.1")

    with pytest.raises(pydantic.ValidationError):
        r4.Reference(reference="foobar")

    with pytest.raises(pydantic.ValidationError):
        r4.Reference(reference="foobar/23")  # foobar is not a resource type


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
        r4._reference_validator(values)
    else:
        with pytest.raises(ValueError):
            r4._reference_validator(values)
