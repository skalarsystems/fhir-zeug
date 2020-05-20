import pytest

from fhirzeug.fhirspec import FHIRSpec


def test_desired_classname(spec: FHIRSpec):
    """Tests if the the enum AccountStatus is correctly used in the Account profile
    """
    clz = spec.profiles["account"].classes[0]
    assert [prop for prop in clz.properties if prop.name == "status"][
        0
    ].desired_classname == "AccountStatus"
