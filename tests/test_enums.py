import pytest


from fhirzeug.generators.python_pydantic.templates.resource_header import DocEnum
from fhirzeug.fhirspec import FHIRSpec


def test_desired_classname(spec: FHIRSpec):
    """Tests if the the enum AccountStatus is correctly used in the Account profile
    """
    clz = spec.profiles["account"].classes[0]
    assert [prop for prop in clz.properties if prop.name == "status"][
        0
    ].desired_classname == "AccountStatus"


class ExampleEnum(str, DocEnum):
    red = "RED", "it is red color"
    blue = (
        "BLUE",
        """it is blue color bla bla
    bla""",
    )


def test_enum_docstring():
    """check to see if The Enum Member docstring set correctly
    """
    red = ExampleEnum.red
    assert red.value == "RED"
    assert red.__doc__ == "it is red color"
