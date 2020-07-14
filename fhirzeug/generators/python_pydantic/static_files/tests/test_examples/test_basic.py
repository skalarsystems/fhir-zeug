from pydantic_fhir import r4


def test_bundle_entry_instanciation() -> None:
    """Test that BundleEntry can be created with an existing Resource."""
    issue = r4.OperationOutcomeIssue(code="not-found", severity="warning")
    outcome = r4.OperationOutcome(issue=[issue])
    entry = r4.BundleEntry(resource=outcome)
    assert entry.resource.issue[0].code == "not-found"
