from typing import Any, Dict
from pydantic import BaseModel

from fhirzeug.generators.python_pydantic.templates.resource_header import DocEnum


class Gender(str, DocEnum):
    male = "MALE", "it is Male docstring"
    female = "FEMALE", "it is female docstring"
    other = "OTHER"


class ExampleModel(BaseModel):
    gender: "Gender"

    class Config:
        @staticmethod
        def schema_extra(schema: Dict[str, Any]) -> None:
            schema["properties"]["gender"]["enum"] = [
                {"value": item.value, "description": item.__doc__} for item in Gender
            ]


def test_enum_member_descriptions():
    enums = ExampleModel.schema()["properties"]["gender"]["enum"]
    male = enums[0]
    other = enums[2]
    assert len(enums) == 3
    assert male["value"] == "MALE"
    assert male["description"] == "it is Male docstring"
    assert other["description"] == "An enumeration."
