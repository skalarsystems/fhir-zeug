import pytest
import pydantic
from pydantic_fhir import r4


def test_bundle_entry_instanciation() -> None:
    """Test that BundleEntry can be created with an existing Resource."""
    issue = r4.OperationOutcomeIssue(code="not-found", severity="warning")
    outcome = r4.OperationOutcome(issue=[issue])
    entry = r4.BundleEntry(resource=outcome)
    assert entry.resource.issue[0].code == "not-found"


def test_int_types() -> None:
    """Test that FHIRInt types are used in Resources.

    `count` must be a FHIRPositiveInt
    `offset` must be a FHIRUnsignedInt
    """
    timing_repeat = r4.TimingRepeat(count=1, offset=1)

    with pytest.raises(pydantic.ValidationError):
        timing_repeat = r4.TimingRepeat(offset=-1)

    with pytest.raises(pydantic.ValidationError):
        timing_repeat = r4.TimingRepeat(offset=1.0)

    with pytest.raises(pydantic.ValidationError):
        timing_repeat = r4.TimingRepeat(count=0)  # noqa : F841


def test_generated_enums() -> None:
    r4.Account(status="active")

    with pytest.raises(pydantic.ValidationError):
        # AccountStatus is a `DocEnum` object.
        account = r4.Account(status="not_a_predefined_status")  # noqa : F841

    r4.TimingRepeat(duration_unit="s")

    with pytest.raises(pydantic.ValidationError):
        # DurationUnit is a typing.Literal field.
        repeat = r4.TimingRepeat(duration_unit="not_a_predefined_unit")  # noqa : F841


def test_empty_list_serialization() -> None:
    """An empty coding must be ignored during serialization.

    - Expected behavior : {}
    - Previous behavior : {"tag" = [None]}
    """
    assert r4.Meta(tag=[r4.Coding()]).dict() == {}


def test_unknown_fields_are_not_allowed() -> None:
    """An error must be thrown if there is an unknown argument provided."""
    with pytest.raises(pydantic.ValidationError):
        r4.Meta(unknown_field=True)


def test_duplicated_entries() -> None:
    """An error must be thrown if there are duplicated key in JSON."""
    r4.from_raw('{"resourceType":"DomainResource"}')
    with pytest.raises(pydantic.ValidationError):
        r4.from_raw(
            '{"resourceType":"DomainResource", "resourceType":"DomainResource"}'
        )


def test_list_instead_of_dict() -> None:
    """An error must be thrown if a list is provided instead of a dict.

    See : https://github.com/skalarsystems/fhirzeug/issues/59
    """
    dict_ = {
        "resourceType": "Observation",
        "status": "final",
        "code": {"coding": [{"system": "test", "code": "test"}]},
    }
    subject = {  # Dictionary -> OK
        "reference": "Patient/475",
        "display": "REF",
    }
    dict_["subject"] = subject
    r4.from_dict(dict_)
    with pytest.raises(pydantic.ValidationError):
        dict_["subject"] = [subject]  # As a list -> not expected
        r4.from_dict(dict_)
