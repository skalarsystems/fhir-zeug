import os


from fhirzeug.fhirspec import (
    FHIRSpec,
    FHIRVersionInfo,
)


def test_writable_profiles(spec: FHIRSpec):
    check = any(
        item in spec.settings.manual_profiles for item in spec.writable_profiles()
    )
    assert check is False


def test_read_version(spec: FHIRSpec):
    path = os.path.join(spec.directory, "version.info")
    version = FHIRVersionInfo(spec, spec.directory).read_version(path)
    assert version == "4.0.1-9346c8cc45"


def test_as_module_name(spec: FHIRSpec):
    module_name = spec.as_module_name("VerificationResult")
    assert module_name == "verificationresult"

    spec.settings.resource_modules_lowercase = False

    module_name = spec.as_module_name("VerificationResult")
    assert module_name == "VerificationResult"


def test_as_class_name(spec: FHIRSpec):
    class_name = spec.as_class_name("role", "Practitioner")
    assert class_name == "PractRole"

    spec.settings.camelcase_classes = True
    class_name = spec.as_class_name("nonexistent")
    assert class_name == "Nonexistent"

    spec.settings.camelcase_classes = False
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


def test_safe_enum_name(spec: FHIRSpec):
    spec.settings.camelcase_enums = True
    assert spec.safe_enum_name("foo_bar", ucfirst=True) == "FooBar"
    assert spec.safe_enum_name("foo_bar", ucfirst=False) == "fooBar"
    assert spec.safe_enum_name("HTTP", ucfirst=True) == "HTTP"
    assert spec.safe_enum_name("HTTP", ucfirst=False) == "HTTP"

    # Real case examples
    assert spec.safe_enum_name("entered-in-error") == "enteredInError"
    assert (
        spec.safe_enum_name("ExampleOnsetType(Reason)Codes")
        == "exampleOnsetTypeReasonCodes"
    )
    assert spec.safe_enum_name("openAtEnd") == "openAtEnd"
    assert spec.safe_enum_name("1-password") == "_1Password"
    assert (
        spec.safe_enum_name("HTTPVerb") == "hTTPVerb"  # <- is this a desired behavior
    )

    spec.settings.camelcase_enums = False
    assert spec.safe_enum_name("foo_bar", ucfirst=True) == "foo_bar"
    assert spec.safe_enum_name("foo_bar", ucfirst=False) == "foo_bar"
    assert spec.safe_enum_name("HTTP", ucfirst=True) == "HTTP"
    assert spec.safe_enum_name("HTTP", ucfirst=False) == "HTTP"

    # Real case examples
    assert spec.safe_enum_name("entered-in-error") == "entered_in_error"
    assert (
        spec.safe_enum_name("ExampleOnsetType(Reason)Codes")
        == "ExampleOnsetType_Reason_Codes"
    )
    assert spec.safe_enum_name("openAtEnd") == "openAtEnd"
    assert spec.safe_enum_name("1-password") == "_1_password"
    assert (
        spec.safe_enum_name("HTTPVerb") == "HTTPVerb"  # <- is this a desired behavior
    )
