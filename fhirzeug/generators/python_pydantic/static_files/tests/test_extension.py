"""Test Extension element."""
import pytest
import pydantic

from pydantic_fhir import r4

ID = "test_id"
URL = "test/example"
NAME = "Queen Elisabeth"
VALUE_INTEGER = 45
VALUE_HUMAN_NAME = r4.HumanName(given=[NAME])


@pytest.fixture
def human_extension() -> r4.Extension:
    """Define an extension with a HumanName as a fixture."""
    return r4.Extension(url=URL, value_human_name=VALUE_HUMAN_NAME)


@pytest.fixture
def integer_extension() -> r4.Extension:
    """Define an extension with an integer as a fixture."""
    return r4.Extension(url=URL, value_integer=VALUE_INTEGER)


@pytest.fixture
def primitive_extension(
    human_extension: r4.Extension, integer_extension: r4.Extension
) -> r4.PrimitiveExtension:
    """Define a primitive extension as a fixture."""
    return r4.PrimitiveExtension(id=ID, extension=[human_extension, integer_extension])


def test_single_value_extension(
    human_extension: r4.Extension, integer_extension: r4.Extension
) -> None:
    """Test an extension with a value is valid."""
    assert isinstance(human_extension, r4.Extension)
    assert isinstance(integer_extension, r4.Extension)


def test_extension_with_subextensions(
    human_extension: r4.Extension, integer_extension: r4.Extension
) -> None:
    """Test an extension with one or several subextensions but no values is valid."""
    r4.Extension(url=URL, extension=[integer_extension])
    r4.Extension(url=URL, extension=[human_extension])
    r4.Extension(url=URL, extension=[integer_extension, human_extension])


def test_multiple_values_extension_forbidden() -> None:
    """Test an extension with multiple values is forbidden."""
    with pytest.raises(pydantic.ValidationError):
        r4.Extension(
            url=URL, value_integer=VALUE_INTEGER, value_human_name=VALUE_HUMAN_NAME
        )


def test_value_and_subextension_forbidden(human_extension: r4.Extension) -> None:
    """Test an extension with a value and a subextension is forbidden."""
    with pytest.raises(pydantic.ValidationError):
        r4.Extension(
            url=URL, value_integer=VALUE_INTEGER, extension=[human_extension],
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
    resource = r4.from_dict(data)
    resource.dict(by_alias=True) == data

    # An empty list of extension is added to an extension containing a value.
    # Extension is still valid since empty list is ignored.
    data["extension"][0]["extension"][1]["extension"] = []  # type: ignore
    r4.from_dict(data)

    # An extension is added to a subextension that already contains a value.
    # Extension is therefore forbidden.
    data["extension"][0]["extension"][1]["extension"] = [{"url": "test/example", "valueInteger": 45}]  # type: ignore
    with pytest.raises(pydantic.ValidationError):
        r4.from_dict(data)


def test_primitive_extension_object(
    human_extension: r4.Extension, integer_extension: r4.Extension
) -> None:
    """Test PrimitiveExtension object."""
    r4.PrimitiveExtension()
    r4.PrimitiveExtension(id=ID)
    r4.PrimitiveExtension(extension=[human_extension, integer_extension])
    r4.PrimitiveExtension(
        id=ID, extension=[human_extension],
    )

    with pytest.raises(pydantic.ValidationError):
        # Extension must be a list
        r4.PrimitiveExtension(extension=human_extension)


def test_primitive_extension_basic_usage(primitive_extension: r4.PrimitiveExtension):
    """Test usage of a PrimitiveExtension."""
    r4.Patient()
    r4.Patient(gender="unknown")
    r4.Patient(gender__extension=primitive_extension)
    r4.Patient(gender="unknown", gender__extension=primitive_extension)


def test_primitive_list_extension_usage(primitive_extension: r4.PrimitiveExtension,):
    """Test usage of primitive list extension."""
    # `given` field is Optional for HumanName
    r4.HumanName()

    # `given` is a `List` field
    # -> So is `given` extension
    r4.HumanName(given=[NAME])
    with pytest.raises(pydantic.ValidationError):
        r4.HumanName(given=NAME)

    r4.HumanName(given__extension=[primitive_extension])
    with pytest.raises(pydantic.ValidationError):
        r4.HumanName(given__extension=primitive_extension)

    # If `given` and `given__extension` are both provided, they must be of same length
    r4.HumanName(given=[NAME], given__extension=[primitive_extension])
    r4.HumanName(
        given=[NAME, NAME], given__extension=[primitive_extension, primitive_extension],
    )

    with pytest.raises(pydantic.ValidationError):
        r4.HumanName(
            given=[NAME], given__extension=[primitive_extension, primitive_extension],
        )

    with pytest.raises(pydantic.ValidationError):
        r4.HumanName(given=[NAME, NAME], given__extension=[primitive_extension])

    with pytest.raises(pydantic.ValidationError):
        r4.HumanName(
            given=[None, NAME],
            given__extension=[primitive_extension, None, primitive_extension],
        )

    # Not the same length because None values are not removed from list
    with pytest.raises(pydantic.ValidationError):
        r4.HumanName(given=[None, NAME, None], given__extension=[primitive_extension])

    # Provide value can be None but not on both sides for the same item
    r4.HumanName(given=[None, NAME], given__extension=[primitive_extension, None])
    r4.HumanName(given=[NAME, NAME], given__extension=[primitive_extension, None])
    with pytest.raises(pydantic.ValidationError):
        r4.HumanName(given=[NAME, None], given__extension=[primitive_extension, None])

    # Both list cannot be empty at the same time
    with pytest.raises(pydantic.ValidationError):
        r4.HumanName(given=[], given__extension=[])


def test_primitive_extension_as_dict():
    """Test resource with a primitive extension is well created and exported."""
    # Test create patient with extended given name.
    data = {
        "resourceType": "Patient",
        "name": [
            {
                "given": ["Queen Elisabeth"],
                "_given": [
                    {
                        "id": "test_id",
                        "extension": [
                            {
                                "url": "test/example",
                                "valueHumanName": {"given": ["Queen Elisabeth"]},
                            },
                            {"url": "test/example", "valueInteger": 45},
                        ],
                    }
                ],
            }
        ],
    }
    patient = r4.from_dict(data)
    assert patient.name[0].given is not None
    assert patient.name[0].given__extension is not None
    assert patient.dict(by_alias=True) == data

    # Test with None values in list.
    data = {
        "given": ["Queen Elisabeth", None],
        "_given": [
            None,
            {
                "id": "test_id",
                "extension": [
                    None,
                    {
                        "url": "test/example",
                        "valueHumanName": {"given": ["Queen Elisabeth"]},
                    },
                    {"url": "test/example", "valueInteger": 45},
                ],
            },
        ],
    }
    human_name = r4.HumanName(**data)
    # Export is different because None value has been removed
    assert human_name.dict(by_alias=True) != data
    # Remove from data the None value and test
    data["_given"][1]["extension"].pop(0)
    assert human_name.dict(by_alias=True) == data

    # Test export in special cases
    assert r4.HumanName(given__extension=[None]).dict(by_alias=True) == {}
    assert r4.HumanName(given=None, given__extension=[None]).dict(by_alias=True) == {}
    assert r4.HumanName(given=[None], given__extension=None).dict(by_alias=True) == {}
    assert r4.HumanName(given=[None]).dict(by_alias=True) == {}
