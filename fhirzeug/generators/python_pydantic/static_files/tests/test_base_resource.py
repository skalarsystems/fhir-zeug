import pytest
import pydantic

from pydantic_fhir import r4


def test_resource_type_not_allowed():
    """Test that resource type value can only be an existing resource name.

    In practice, this value must never be set manually.
    """
    resource = r4.FHIRAbstractResource()
    resource = r4.FHIRAbstractResource(resource_type="DomainResource")

    with pytest.raises(pydantic.ValidationError):
        resource = r4.FHIRAbstractResource(resource_type="FooBar")  # noqa : F841


def test_resource_type_not_provided():
    """Test that if resource_type is not provided, exception is raised."""

    data = {
        "resourceType": "HealthcareService",
        "id": "example",
        "contained": [{"resourceType": "", "id": "anotherexample"}],
    }

    with pytest.raises(pydantic.ValidationError):
        resource = r4.from_dict(data["contained"][0]["resourceType"])

    with pytest.raises(pydantic.ValidationError):
        resource = r4.from_dict(data)

    data["contained"][0]["resourceType"] = "Patient"
    resource = r4.from_dict(data)
    resource = r4.from_dict(data["contained"][0])  # noqa : F841
