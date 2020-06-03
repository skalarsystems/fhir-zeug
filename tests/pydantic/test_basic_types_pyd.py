import pytest
import pydantic
import typing
import base64

from fhirzeug.generators.python_pydantic.templates.fhir_basic_types import (
    FHIRDate,
    FHIRDateTime,
    FHIRTime,
    FHIRInstant,
    FHIRBase64Binary,
    FHIRId,
    FHIROid,
)


class TestModel(pydantic.BaseModel):
    """A Test class to check all basic datatypes."""

    date: typing.Optional[FHIRDate]
    datetime: typing.Optional[FHIRDateTime]
    time: typing.Optional[FHIRTime]
    instant: typing.Optional[FHIRInstant]
    base64: typing.Optional[FHIRBase64Binary]
    oid: typing.Optional[FHIROid]
    fhir_id: typing.Optional[FHIRId]


def test_fhirdate():
    """Test FHIRDate
    https://www.hl7.org/fhir/datatypes.html#date"""
    with pytest.raises(pydantic.ValidationError):
        model = TestModel(date="foo")
    with pytest.raises(pydantic.ValidationError):
        model = TestModel(date="24:00")
    model = TestModel(date="1905-08-23")


def test_fhirdatetime():
    """Test FHIRDateTime
    https://www.hl7.org/fhir/datatypes.html#dateTime"""
    with pytest.raises(pydantic.ValidationError):
        model = TestModel(datetime="foo")
    with pytest.raises(pydantic.ValidationError):
        model = TestModel(datetime="24:00")
    model = TestModel(datetime="1905-08-23")


def test_fhirtime():
    """Test FHIRTime
    https://www.hl7.org/fhir/datatypes.html#time"""
    with pytest.raises(pydantic.ValidationError):
        model = TestModel(time="foo")
    with pytest.raises(pydantic.ValidationError):
        model = TestModel(time="24:00")
    model = TestModel(time="17:00:00")


def test_fhirinstant():
    """Test FHIRInstant
    https://www.hl7.org/fhir/datatypes.html#instant"""
    with pytest.raises(pydantic.ValidationError):
        model = TestModel(instant="foo")
    with pytest.raises(pydantic.ValidationError):
        model = TestModel(instant="24:00")
    model = TestModel(instant="2017-01-01T00:00:00Z")
    model = TestModel(instant="2015-02-07T13:28:17.239+02:00")


def test_fhirbase64binary():

    """Test FHIRBase64Binary
    https://www.hl7.org/fhir/datatypes.html#base64binary"""
    message = "Foo Bar"
    message_bytes = message.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode("ascii")
    model = TestModel(base64=base64_message)

    with pytest.raises(pydantic.ValidationError):
        model = TestModel(base64=message)


def test_fhiroid():

    """Test FHIROid
    https://www.hl7.org/fhir/datatypes.html#oid"""

    model = TestModel(oid="urn:oid:1.2.3.4.5")
    with pytest.raises(pydantic.ValidationError):
        model = TestModel(oid="foo")


def test_fhirid():
    """Test FHIRId
    https://www.hl7.org/fhir/datatypes.html#id"""

    model = TestModel(fhir_id="foo.bar")
    with pytest.raises(pydantic.ValidationError):
        model = TestModel(fhir_id="?")
