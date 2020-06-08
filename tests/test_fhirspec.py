import os
import pytest


from fhirzeug.fhirspec import FHIRSpec, FHIRStructureDefinitionStructure, FHIRVersionInfo
from fhirzeug.fhirclass import FHIRClass


def test_writable_profiles(spec: FHIRSpec):
    check =  any(item in spec.settings.manual_profiles for item in spec.writable_profiles())
    assert check == False


def test_read_version(spec: FHIRSpec):
    path = os.path.join(spec.directory, 'version.info')
    version = FHIRVersionInfo(spec, spec.directory).read_version(path)
    assert version == '4.0.1-9346c8cc45'

def test_as_module_name(spec: FHIRSpec):
    module_name = spec.as_module_name('VerificationResult')
    assert module_name == 'verificationresult'

    spec.settings.resource_modules_lowercase = False

    module_name = spec.as_module_name('VerificationResult')
    assert module_name == 'VerificationResult'