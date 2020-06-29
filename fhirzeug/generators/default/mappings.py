import typing

# Mappings for the FHIR class generator.
#
# This should be useable as-is for Python classes.

# Which class names to map to resources and elements
classmap: typing.Dict[str, str] = {
    "Any": "Resource",
    "Practitioner.role": "PractRole",  # to avoid Practinioner.role and PractitionerRole generating the same class
    "boolean": "bool",
    "integer": "int",
    "positiveInt": "int",
    "unsignedInt": "int",
    "date": "FHIRDate",
    "dateTime": "FHIRDateTime",
    "instant": "FHIRInstant",
    "time": "FHIRTime",
    "decimal": "decimal.Decimal",
    "string": "str",
    "markdown": "str",
    "id": "FHIRId",
    "code": "FHIRCode",  # for now we're not generating enums for these
    "uri": "str",
    "url": "str",
    "canonical": "str",
    "oid": "FHIROid",
    "uuid": "str",
    "xhtml": "str",
    "base64Binary": "FHIRBase64Binary",
}

# Classes to be replaced with different ones at resource rendering time
replacemap: typing.Dict[str, str] = {
    # "Reference": "FHIRReference",  # `FHIRReference` adds dereferencing capabilities
}

# Which class names are native to the language (or can be treated this way)
natives = ["bool", "int", "float", "str", "dict", "decimal"]

# Which classes are to be expected from JSON decoding
jsonmap: typing.Dict[str, str] = {
    "str": "str",
    "int": "int",
    "bool": "bool",
    "decimal.Decimal": "float",
    "FHIRDate": "str",
}
jsonmap_default = "dict"

# Properties that need to be renamed because of language keyword conflicts
reservedmap: typing.Dict[str, str] = {
    "for": "for_",
    "from": "from_",
    "class": "class_",
    "import": "import_",
    "global": "global_",
    "assert": "assert_",
    "except": "except_",
    "in": "in_",
    "del": "del_",
    "return": "return_",
    "as": "as_",
    "not": "not_",
    "pass": "pass_",
}

# For enum codes where a computer just cannot generate reasonable names
enum_map: typing.Dict[str, str] = {
    "=": "eq",
    "!=": "ne",
    "<": "lt",
    "<=": "lte",
    ">": "gt",
    ">=": "gte",
    "*": "max",
}

# If you want to give specific names to enums based on their URI
enum_namemap: typing.Dict[str, str] = {
    "http://terminology.hl7.org/CodeSystem/composition-altcode-kind": "CompositionAltcodeKind",
    "http://terminology.hl7.org/CodeSystem/codesystem-altcode-kind": "CodesystemAltcodeKind",
    "http://hl7.org/fhir/contract-security-category": "ContractSecurityCategoryCodes",
    "http://hl7.org/fhir/contract-security-classification": "ContractSecurityClassificationCodes",
    "http://hl7.org/fhir/contract-scope": "ContractScopeCodes",
    "http://hl7.org/fhir/device-definition-status": "FHIRDeviceDefinitionStatus",
    "http://hl7.org/fhir/device-status": "FHIRDeviceStatus",
    "http://hl7.org/fhir/CodeSystem/medication-statement-status": "MedicationStatementStatusCodes",
    "http://hl7.org/fhir/CodeSystem/medication-status": "MedicationStatusCodes",
    "http://terminology.hl7.org/CodeSystem/observation-category": "ObservationCategoryCodes",
    "http://hl7.org/fhir/secondary-finding": "SecondaryFindingCodes",
    # PractinionerRole is also a DomainResource
    "http://terminology.hl7.org/CodeSystem/practitioner-role": "PractitionerRoleCodes",
}

# If certain CodeSystems don't need to generate an enum
enum_ignore: typing.Dict[str, str] = {
    # 'http://hl7.org/fhir/resource-type-link',
}
