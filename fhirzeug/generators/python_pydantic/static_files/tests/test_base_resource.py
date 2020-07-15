import pytest
import pydantic

from pydantic_fhir import r4


def test_resource_type():
    """Test that resource type value can only be an existing resource name.

    In practice, this value must never be set manually.
    """
    resource = r4.FHIRAbstractResource()
    resource = r4.FHIRAbstractResource(resource_type="DomainResource")

    with pytest.raises(pydantic.ValidationError):
        resource = r4.FHIRAbstractResource(resource_type="FooBar")  # noqa : F841
