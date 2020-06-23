# Mappings for the FHIR class generator.
#
# This should be useable as-is for Python classes.

# Which class names to map to resources and elements
classmap = {
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
replacemap = {
    # "Reference": "FHIRReference",  # `FHIRReference` adds dereferencing capabilities
}

# Which class names are native to the language (or can be treated this way)
natives = ["bool", "int", "float", "str", "dict", "decimal"]

# Which classes are to be expected from JSON decoding
jsonmap = {
    "str": "str",
    "int": "int",
    "bool": "bool",
    "decimal.Decimal": "float",
    "FHIRDate": "str",
}
jsonmap_default = "dict"

# Properties that need to be renamed because of language keyword conflicts
reservedmap = {
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
enum_map = {
    "=": "eq",
    "!=": "ne",
    "<": "lt",
    "<=": "lte",
    ">": "gt",
    ">=": "gte",
    "*": "max",
}

# If you want to give specific names to enums based on their URI
enum_namemap = {
    # 'http://hl7.org/fhir/coverage-exception': 'CoverageExceptionCodes',
}

# If certain CodeSystems don't need to generate an enum
enum_ignore = {
    # 'http://hl7.org/fhir/resource-type-link',
}
