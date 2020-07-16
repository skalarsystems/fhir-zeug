import base64
import decimal
import typing


import pydantic
import pytest


from fhirzeug.generators.python_pydantic.templates.fhir_basic_types import (
    FHIRString,
    FHIRRequiredString,
    FHIRDate,
    FHIRDateTime,
    FHIRTime,
    FHIRInstant,
    FHIRBase64Binary,
    FHIRId,
    FHIROid,
    FHIRInt,
    FHIRUnsignedInt,
    FHIRPositiveInt,
)


class ExampleModel(pydantic.BaseModel):
    """A Test class to check all basic datatypes."""

    string: typing.Optional[FHIRString]
    date: typing.Optional[FHIRDate]
    datetime: typing.Optional[FHIRDateTime]
    time: typing.Optional[FHIRTime]
    instant: typing.Optional[FHIRInstant]
    base64: typing.Optional[FHIRBase64Binary]
    oid: typing.Optional[FHIROid]
    fhir_id: typing.Optional[FHIRId]
    decimal: typing.Optional[decimal.Decimal]
    fhir_int: typing.Optional[FHIRInt]
    fhir_unsigned_int: typing.Optional[FHIRUnsignedInt]
    fhir_positive_int: typing.Optional[FHIRPositiveInt]


def test_fhirstring():
    """Test FHIRString
    https://www.hl7.org/fhir/datatypes.html#string"""
    model = ExampleModel(string="wow")
    assert model.string == "wow"
    model = ExampleModel(string="    foo")
    assert model.string == "foo"
    model = ExampleModel(string="bar    ")
    assert model.string == "bar"
    model = ExampleModel(string="   baz \n ")
    assert model.string == "baz"
    model = ExampleModel(string="  ")
    assert model.string == ""


def test_fhirrequiredstring():
    """Test FHIRRequiredString

    It's a variant of FHIRString which requires at least one non-whitespace
    character.
    """

    class ExampleModelWithRequiredString(pydantic.BaseModel):
        required_string = FHIRRequiredString()

    with pytest.raises(pydantic.ValidationError):
        ExampleModelWithRequiredString(required_string=None)
    with pytest.raises(pydantic.ValidationError):
        ExampleModelWithRequiredString(required_string="")
    with pytest.raises(pydantic.ValidationError):
        ExampleModelWithRequiredString(required_string=" \n\t\r  ")
    model = ExampleModel(string="wow")
    assert model.string == "wow"
    model = ExampleModel(string="    foo")
    assert model.string == "foo"


def test_fhirdate():
    """Test FHIRDate
    https://www.hl7.org/fhir/datatypes.html#date"""
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(date="foo")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(date="24:00")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(date="1973-06-33")
    model = ExampleModel(date="2018")
    model = ExampleModel(date="1973-06")
    model = ExampleModel(date="1905-08-23")  # noqa : F841


def test_fhirdatetime():
    """Test FHIRDateTime
    https://www.hl7.org/fhir/datatypes.html#dateTime"""
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(datetime="foo")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(datetime="24:00")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(datetime="2015-02-07T13:28:17")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(datetime="1905-08-33")
    model = ExampleModel(datetime="2018")
    model = ExampleModel(datetime="1973-06")
    model = ExampleModel(datetime="1905-08-23")
    model = ExampleModel(datetime="2015-02-07T13:28:17-05:00")
    model = ExampleModel(datetime="2017-01-01T00:00:00.000Z")  # noqa : F841


def test_fhirtime():
    """Test FHIRTime
    https://www.hl7.org/fhir/datatypes.html#time"""
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(time="foo")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(time="24:00")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(time="13:28:17-05:00")
    model = ExampleModel(time="17:00:00")  # noqa : F841


def test_fhirinstant():
    """Test FHIRInstant
    https://www.hl7.org/fhir/datatypes.html#instant"""
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(instant="foo")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(instant="24:00")
    model = ExampleModel(instant="2017-01-01T00:00:00Z")
    model = ExampleModel(instant="2015-02-07T13:28:17.239+02:00")  # noqa : F841


def test_fhirbase64binary():
    """Test FHIRBase64Binary
    https://www.hl7.org/fhir/datatypes.html#base64binary"""

    message = "Foo Bar"
    message_bytes = message.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode("ascii")
    model = ExampleModel(base64=base64_message)
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(base64=message)

    model = ExampleModel(base64="2jmj7l5rSw0yVb/vlWAYkK/YBwk=")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(base64="2jmj7l5rSw0yVb/vlWAYkK/YBwk")  # noqa : F841


def test_fhiroid():
    """Test FHIROid
    https://www.hl7.org/fhir/datatypes.html#oid"""

    model = ExampleModel(oid="urn:oid:1.2.3.4.5")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(oid="foo")  # noqa : F841


def test_fhirid():
    """Test FHIRId
    https://www.hl7.org/fhir/datatypes.html#id"""

    model = ExampleModel(fhir_id="foo.bar")
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_id="?")  # noqa : F841


def test_decimal():
    """Test FHIRDecimal
    https://www.hl7.org/fhir/datatypes.html#decimal"""

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(decimal="FOO")
    model = ExampleModel(decimal=3.14000000000000012434497875801)  # noqa : F841


def test_fhir_int():
    """Test FHIRInt
    """
    model = ExampleModel(fhir_int=-123456)
    model = ExampleModel(fhir_int="-123456")
    model = ExampleModel(fhir_int=0)
    model = ExampleModel(fhir_int="0")
    model = ExampleModel(fhir_int=123456)
    model = ExampleModel(fhir_int="123456")
    assert model.fhir_int == 123456

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_int=1.234)

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_int=0.0)

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_int="-1.234")


def test_fhir_unsigned_int():
    """Test FHIRUnsignedInt
    """
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_unsigned_int=-123456)

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_unsigned_int="-123456")

    model = ExampleModel(fhir_unsigned_int=0)
    model = ExampleModel(fhir_unsigned_int="0")
    model = ExampleModel(fhir_unsigned_int=123456)
    model = ExampleModel(fhir_unsigned_int="123456")
    assert model.fhir_unsigned_int == 123456

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_unsigned_int=1.234)

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_unsigned_int=0.0)

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_unsigned_int="-1.234")


def test_fhir_positive_int():
    """Test FHIRUnsignedInt
    """
    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_positive_int=-123456)

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_positive_int="-123456")

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_positive_int=0)

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_positive_int="0")

    model = ExampleModel(fhir_positive_int=123456)
    model = ExampleModel(fhir_positive_int="123456")
    assert model.fhir_positive_int == 123456

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_positive_int=1.234)

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_positive_int=0.0)

    with pytest.raises(pydantic.ValidationError):
        model = ExampleModel(fhir_positive_int="-1.234")
