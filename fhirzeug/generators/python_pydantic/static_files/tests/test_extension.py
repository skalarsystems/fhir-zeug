"""Test Extension element."""
import pytest
import pydantic

from pydantic_fhir import r4


def test_extension_validation() -> None:
    """Test Extension element validation."""
    url = "test/example"
    value_integer = 45
    value_human_name = r4.HumanName(given=["Queen Elisabeth"])

    integer_extension = r4.Extension(url=url, value_integer=value_integer)
    human_name_extension = r4.Extension(url=url, value_human_name=value_human_name)

    r4.Extension(url=url, extension=[integer_extension])
    r4.Extension(url=url, extension=[human_name_extension])
    r4.Extension(url=url, extension=[integer_extension, human_name_extension])

    with pytest.raises(pydantic.ValidationError):
        r4.Extension(
            url=url, value_integer=value_integer, value_human_name=value_human_name
        )

    with pytest.raises(pydantic.ValidationError):
        r4.Extension(
            url=url, value_integer=value_integer, extension=[human_name_extension]
        )


def test_extension_in_a_domain_resource() -> None:
    """Test Extension element validation, within a DomainResource."""
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

    data["extension"][0]["extension"][1]["extension"] = []  # type: ignore
    r4.from_dict(data)

    data["extension"][0]["extension"][1]["extension"] = [{"url": "test/example", "valueInteger": 45}]  # type: ignore
    with pytest.raises(pydantic.ValidationError):
        r4.from_dict(data)
