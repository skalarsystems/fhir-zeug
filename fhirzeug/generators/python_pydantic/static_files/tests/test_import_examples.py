import json
from pathlib import Path
import pytest

from pydantic_fhir import r4

NOT_WORKING = {
    "activitydefinition-example.json",
    "activitydefinition-servicerequest-example.json",
    "plandefinition-example.json",
    "relatedperson-example.json",
    "patient-example.json",
    "activitydefinition-predecessor-example.json",
}


def test_read(fhir_file: Path):

    with fhir_file.open() as f_in:
        doc = json.load(f_in)

    assert r4.from_dict(doc) is not None


def test_read_write(fhir_file: Path):
    """ This verifies if a written model equals to the read version"""

    if fhir_file.name in NOT_WORKING:
        pytest.skip("test disabled")

    # load
    with fhir_file.open() as f_in:
        doc = json.load(f_in)
    obj = r4.from_dict(doc)

    # write
    json_str = obj.json(by_alias=True, exclude_unset=True)
    obj_parsed = r4.from_dict(json.loads(json_str))

    # load again
    assert obj_parsed == obj

    assert json.loads(json_str) == doc
