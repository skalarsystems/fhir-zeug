import json
from pathlib import Path

from pydantic_fhir import r4


def test_read(fhir_file: Path):

    with fhir_file.open() as f_in:
        doc = json.load(f_in)

    assert r4.from_dict(doc) is not None
