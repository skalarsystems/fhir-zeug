import os


from fhirzeug.fhirspec import (
    FHIRSpec,
    FHIRVersionInfo,
)


def test_writable_profiles(spec: FHIRSpec):
    check = any(
        item in spec.generator_config.manual_profiles
        for item in spec.writable_profiles()
    )
    assert check is False


def test_read_version(spec: FHIRSpec):
    path = os.path.join(spec.directory, "version.info")
    version = FHIRVersionInfo(spec, spec.directory).read_version(path)
    assert version == "4.0.1-9346c8cc45"


def test_as_module_name(spec: FHIRSpec):
    module_name = spec.as_module_name("VerificationResult")
    assert module_name == "verificationresult"

    spec.generator_config.naming_rules.resource_modules_lowercase = False

    module_name = spec.as_module_name("VerificationResult")
    assert module_name == "VerificationResult"


def test_as_class_name(spec: FHIRSpec):
    class_name = spec.as_class_name("role", "Practitioner")
    assert class_name == "PractRole"

    spec.generator_config.naming_rules.camelcase_classes = True
    class_name = spec.as_class_name("nonexistent")
    assert class_name == "Nonexistent"

    spec.generator_config.naming_rules.camelcase_classes = False
    class_name = spec.as_class_name("nonexistent")
    assert class_name == "nonexistent"


def test_class_name_for_type_if_property(spec: FHIRSpec):
    class_name = spec.class_name_for_type_if_property("")
    assert class_name is None


def test_class_name_for_profile(spec: FHIRSpec):
    profile_name = "http://hl7.org/fhir/Profile/MyProfile"
    class_name = "MyProfile"
    assert spec.class_name_for_profile(None) is None
    assert spec.class_name_for_profile(profile_name) == class_name
    assert spec.class_name_for_profile([profile_name]) == [class_name]
