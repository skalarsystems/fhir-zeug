import pytest


from fhirzeug.fhirspec import FHIRSpec


def test_writable_profiles(spec: FHIRSpec):
  check =  any(item in spec.settings.manual_profiles for item in spec.writable_profiles())
  assert check == False
