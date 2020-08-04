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
    
    - Expected behavior : "tag" = []
    - Previous behavior : "tag" = [None]
    """
    assert r4.Meta(tag=[r4.Coding()]) == {"tag": []}

