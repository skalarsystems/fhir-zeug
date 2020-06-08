import os
import pytest


from fhirzeug.fhirspec import FHIRSpec, FHIRVersionInfo


def test_writable_profiles(spec: FHIRSpec):
  check =  any(item in spec.settings.manual_profiles for item in spec.writable_profiles())
  assert check == False


def test_read_version(spec: FHIRSpec):
  path = os.path.join(spec.directory, 'version.info')
  version = FHIRVersionInfo(spec, spec.directory).read_version(path)
  assert version == '4.0.1-9346c8cc45'
