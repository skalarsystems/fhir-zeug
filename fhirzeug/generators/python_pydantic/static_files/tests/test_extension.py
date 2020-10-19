"""Test Extension element."""
import pytest
import pydantic

from pydantic_fhir import r4


URL = "test/example"
VALUE_INTEGER = 45
VALUE_HUMAN_NAME = r4.HumanName(given=["Queen Elisabeth"])


def test_single_value_extension() -> None:
    """Test an extension with a value is valid."""
    r4.Extension(url=URL, value_integer=VALUE_INTEGER)
    r4.Extension(url=URL, value_human_name=VALUE_HUMAN_NAME)


def test_extension_with_subextensions() -> None:
    """Test an extension with one or several subextensions but no values is valid."""
    r4.Extension(
        url=URL, extension=[r4.Extension(url=URL, value_integer=VALUE_INTEGER)],
    )
    r4.Extension(
        url=URL, extension=[r4.Extension(url=URL, value_human_name=VALUE_HUMAN_NAME)],
    )
    r4.Extension(
        url=URL,
        extension=[
            r4.Extension(url=URL, value_integer=VALUE_INTEGER),
            r4.Extension(url=URL, value_human_name=VALUE_HUMAN_NAME),
        ],
    )


def test_multiple_values_extension_forbidden() -> None:
    """Test an extension with multiple values is forbidden."""
    with pytest.raises(pydantic.ValidationError):
        r4.Extension(
            url=URL, value_integer=VALUE_INTEGER, value_human_name=VALUE_HUMAN_NAME
        )


def test_value_and_subextension_forbidden() -> None:
    """Test an extension with a value and a subextension is forbidden."""
    with pytest.raises(pydantic.ValidationError):
        r4.Extension(
            url=URL,
            value_integer=VALUE_INTEGER,
            extension=[r4.Extension(url=URL, value_human_name=VALUE_HUMAN_NAME)],
        )


def test_extension_in_a_domain_resource() -> None:
    """Test Extension validation within a DomainResource at multiple levels."""
    # Data is a valid definition of an extended domain resource
    data = {
        "resourceType": "DomainResource",
        "extension": [
            {
                "extension": [
                    {"url": "test/example", "valueInteger": 45},
                    {
                        "url": "test/example",
                        "valueHumanName": {"given": ["Queen Elisabeth"]},
                    },
                ],
                "url": "test/example",
            }
        ],
    }
    r4.from_dict(data)

    # An empty list of extension is added to an extension containing a value.
    # Extension is still valid since empty list is ignored.
    data["extension"][0]["extension"][1]["extension"] = []  # type: ignore
    r4.from_dict(data)

    # An extension is added to a subextension that already contains a value.
    # Extension is therefore forbidden.
    data["extension"][0]["extension"][1]["extension"] = [{"url": "test/example", "valueInteger": 45}]  # type: ignore
    with pytest.raises(pydantic.ValidationError):
        r4.from_dict(data)
