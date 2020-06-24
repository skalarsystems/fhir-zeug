[![GitHub license](https://img.shields.io/github/license/skalarsystems/fhirzeug.svg)](./LICENSE.txt)
[![CI](https://github.com/skalarsystems/fhirzeug/workflows/CI/badge.svg)](https://github.com/skalarsystems/fhirzeug/actions?query=workflow%3ACI)
[![Codecov](https://codecov.io/gh/skalarsystems/fhirzeug/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/gh/skalarsystems/fhirzeug/branch/master)

# FHIR Zeug - A FHIR Spec Compiler

(forked from https://github.com/smart-on-fhir/fhir-parser)

## Why a fork?

The original project seemed to abandoned and its structure was not quite pythonic. The work which
has been done was great and we wanted to continue development here. We wanted to have a more
self-contained project, which already has the definitions for the languages on board.

Our main support goals are Python (3.8) with [pydantic](https://github.com/samuelcolvin/pydantic/)
and [FHIR R4](https://hl7.org/fhir/R4/).

This work is licensed under the [APACHE license][license].
FHIR® is the registered trademark of [HL7](http://hl7.org) and is used with the permission of HL7.

## Usage

The `fhir_zeug.cli` module is the central CLI utility included. In an installed environment it can
be called with

Make sure you have the ouput not in the project directory otherwise you will run into issues with
poetry.

```
poetry run fhirzeug  --output-directory ../pydantic-fhir --generator python_pydantic
```

It will:

- Download the [FHIR specification][fhir]
- Parse it
- Generate
  - source files for python pydantic
  - a full python package also available (here)[https://pypi.org/project/pydantic-fhir/]).

# Obsolete

This script does its job for the most part, but it doesn't yet handle all FHIR peculiarities and there's no guarantee the output is correct or complete.

### How are property names determined?

Every “property” of a class, meaning every `element` in a profile snapshot, is represented as a `FHIRStructureDefinitionElement` instance.
If an element itself defines a class, e.g. `Patient.animal`, calling the instance's `as_properties()` method returns a list of `FHIRClassProperty` instances – usually only one – that indicates a class was found in the profile.
The class of this property is derived from `element.type`, which is expected to only contain one entry, in this matter:

- If _type_ is `BackboneElement`, a class name is constructed from the parent element (in this case _Patient_) and the property name (in this case _animal_), camel-cased (in this case _PatientAnimal_).
- If _type_ is `*`, a class for all classes found in settings``star_expand_types` is created
- Otherwise, the type is taken as-is (e.g. _CodeableConcept_) and mapped according to mappings' `classmap`, which is expected to be a valid FHIR class.

> TODO: should `http://hl7.org/fhir/StructureDefinition/structuredefinition-explicit-type-name` be respected?

[license]: ./LICENSE.txt
[hl7]: http://hl7.org/
[fhir]: http://www.hl7.org/implement/standards/fhir/
[jinja]: http://jinja.pocoo.org/
