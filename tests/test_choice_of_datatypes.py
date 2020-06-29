"""A few elements have a choice of more than one data type for their content.

 All such elements have a name that takes the form nnn[x]. The "nnn" part of the name is constant,
 and the "[x]" is replaced with the title-cased name of the type that is actually used. The table
 view shows each of these names explicitly.

Elements that have a choice of data type cannot repeat - they must have a maximum cardinality of 1.
When constructing an instance of an element with a choice of types, the authoring system must create
 a single element with a data type chosen from among the list of permitted data types.

Note: In object-orientated implementations, this is naturally represented as a polymorphic property.
 However this is not necessary and the correct implementation varies according to the particular
 features of the language. In XML schema, these become an xs:choice of element. To help with code
 generation, a list of choice elements is published.


These tests here use the capability statement because it is relatively small to isolate the cases
quite well.
"""


from fhirzeug.fhirspec import FHIRSpec


# the validator needs to be moved into a pydantic generator section


def test_cot(spec: FHIRSpec):
    """Test the hypothesis for the useagecontext"""
    clz = spec.profiles["usagecontext"].classes[0]

    assert set(clz.choice_properties["value"]) == {
        "valueRange",
        "valueReference",
        "valueQuantity",
        "valueCodeableConcept",
    }
