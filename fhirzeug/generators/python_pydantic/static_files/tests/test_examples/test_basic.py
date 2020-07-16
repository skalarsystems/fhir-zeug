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
