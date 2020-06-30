import json
import typing
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

REQUIRES_WHITESPACE_PREPROCESSING = {
    "measure-cms146-example.json",
    "medicinalproductpackaged-example.json",
    "plandefinition-protocol-example.json",
}


def preprocess_whitespace(obj: typing.Any) -> typing.Any:
    if isinstance(obj, str):
        return obj.strip()

    # we should worry only about JSON types here
    if isinstance(obj, list):
        return [preprocess_whitespace(item) for item in obj]

    if isinstance(obj, dict):
        return {key: preprocess_whitespace(value) for key, value in obj.items()}

    return obj


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

    if fhir_file.name in REQUIRES_WHITESPACE_PREPROCESSING:
        doc = preprocess_whitespace(doc)

    obj = r4.from_dict(doc)

    # write
    json_str = obj.json(by_alias=True, exclude_unset=True)
    obj_parsed = r4.from_dict(json.loads(json_str))

    # load again
    assert obj_parsed == obj

    assert json.loads(json_str) == doc
