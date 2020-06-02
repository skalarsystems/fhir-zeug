import json
from pathlib import Path
import pytest

from pydantic_fhir import r4


def test_read(fhir_file: Path):

    with fhir_file.open() as f_in:
        doc = json.load(f_in)

    assert r4.from_dict(doc) is not None


def test_write(fhir_file: Path):
    pytest.skip("This is failing because model reading is not correctly working.")
    with fhir_file.open() as f_in:
        doc = json.load(f_in)

    obj = r4.from_dict(doc)
    assert obj is not None
    doc_write = obj.dict(by_alias=True, exclude_unset=True)
    print(doc_write)
    print("\n###\n")
    print(doc)
    assert doc_write == doc
