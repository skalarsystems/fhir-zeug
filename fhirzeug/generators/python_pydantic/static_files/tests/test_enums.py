from pydantic.schema import schema
import pytest
from pydantic_fhir import r4


def test_enums_in_resource():
    """Test schema on a real example with an enum field."""
    status_enum = r4.StructureMap.schema()["properties"]["status"]["enum"]
    assert sorted(status_enum, key=lambda x: x["value"]) == sorted(
        [
            {"value": item.value, "description": item.__doc__}
            for item in r4.PublicationStatus
        ],
        key=lambda x: x["value"],
    )
