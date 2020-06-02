import json
from pathlib import Path
import pytest

from pydantic_fhir import r4

# all are disabled because extensions are not implemented:
# https://github.com/skalarsystems/fhirzeug/issues/13
NOT_WORKING = {
    "activitydefinition-example.json",  # _event
    "activitydefinition-servicerequest-example.json",  # _event
    "plandefinition-example.json",  # _event
    "relatedperson-example.json",  # _name
    "patient-example.json",  # _name
    "activitydefinition-predecessor-example.json",  # _event
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
