import re
import json
import typing
from pathlib import Path
from collections import Counter

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
    "diagnosticreport-hla-genetics-results-example.json",  # invalid reference field
}

# Some .json files require preprocessing because they have whitespace at the end
# of strings, which is removed by pydantic-fhir.
REQUIRES_WHITESPACE_PREPROCESSING = {
    "measure-cms146-example.json",
    "medicinalproductpackaged-example.json",
    "plandefinition-protocol-example.json",
}


def preprocess_whitespace(obj: typing.Any) -> typing.Any:
    """Remove the leading and trailing whitespace from strings in the object."""
    if isinstance(obj, str):
        return obj.strip()

    # we should worry only about JSON types here
    if isinstance(obj, list):
        return [preprocess_whitespace(item) for item in obj]

    if isinstance(obj, dict):
        return {key: preprocess_whitespace(value) for key, value in obj.items()}

    return obj


def test_read(fhir_file: Path):
    """ Test verifies if model is correctly read"""

    if fhir_file.name in NOT_WORKING:
        pytest.skip("test disabled")

    with fhir_file.open() as f_in:
        doc = json.load(f_in)

    assert r4.from_dict(doc) is not None


def test_read_write(fhir_file: Path):
    """ This verifies if a written model equals to the read version"""

    if fhir_file.name in NOT_WORKING:
        pytest.skip("test disabled")

    # load
    with fhir_file.open() as f_in:
        json_in = f_in.read()
        doc = r4.json_loads(json_in)

    if fhir_file.name in REQUIRES_WHITESPACE_PREPROCESSING:
        doc = preprocess_whitespace(doc)

    obj = r4.from_dict(doc)

    # write
    json_str = obj.json(by_alias=True, exclude_unset=True)
    obj_parsed = r4.from_dict(json.loads(json_str))

    # load again
    assert obj_parsed == obj

    assert r4.json_loads(json_str) == doc

    # Check if both strings have same length
    norm_in = _normalize(json_in)
    norm_out = _normalize(json_str)
    assert len(norm_in) == len(norm_out)

    # Check if both strings contains exactly the same characters
    # If both strings have same length and same characters, we assume serialization is good
    counter_in = Counter(norm_in)
    counter_out = Counter(norm_out)
    assert counter_in == counter_out


def _normalize(s):
    """Normalize a json string to be comparable"""
    # Remove all whitespaces and newlines
    s = "".join(s.split())

    # Replace all unicode characters
    for match in set(re.findall(r"(\\u[\d|a-f]{4})", s)):
        s = s.replace(match, eval(f"'{match}'"))
    return s
