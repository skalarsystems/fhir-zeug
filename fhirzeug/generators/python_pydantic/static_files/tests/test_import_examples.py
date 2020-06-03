import json
from pathlib import Path
import pytest

from pydantic_fhir import r4

NOT_WORKING = {
    "xds-example.json",
    "activitydefinition-servicerequest-example.json",
    "parameters-example.json",
    "guidanceresponse-example.json",
    "bundle-example.json",
    "activitydefinition-example.json",
    "healthcareservice-example.json",
    "plandefinition-example.json",
    "activitydefinition-medicationorder-example.json",
    "diagnosticreport-example.json",
    "requestgroup-example.json",
    "medicationknowledge-example.json",
    "relatedperson-example.json",
    "careplan-example.json",
    "plandefinition-protocol-example.json",
    "requestgroup-kdn5-example.json",
    "measurereport-cms146-cat2-example.json",
    "careteam-example.json",
    "measurereport-cms146-cat3-example.json",
    "diagnosticreport-hla-genetics-results-example.json",
    "measurereport-cms146-cat1-example.json",
    "documentreference-example.json",
    "plandefinition-options-example.json",
    "patient-example.json",
    "documentmanifest-example.json",
    "questionnaireresponse-example.json",
    "specimen-example.json",
    "activitydefinition-predecessor-example.json",
}


def test_read(fhir_file: Path):

    with fhir_file.open() as f_in:
        doc = json.load(f_in)

    assert r4.from_dict(doc) is not None


def test_write(fhir_file: Path):
    if fhir_file.name in NOT_WORKING:
        pytest.skip("test disabled")
    with fhir_file.open() as f_in:
        doc = json.load(f_in)

    obj = r4.from_dict(doc)
    assert obj is not None
    doc_write = obj.dict(by_alias=True, exclude_unset=True)
    assert doc_write == doc
