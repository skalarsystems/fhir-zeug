import re
import pydantic


def exact_regex(regex):
    return r"\A" + regex.lstrip(r"\A").rstrip(r"\Z") + r"\Z"


def exact_regex_constr(**kwargs):
    if kwargs.get("regex") is not None:
        kwargs["regex"] = exact_regex(kwargs["regex"])
    return pydantic.constr(**kwargs)


FHIRString = pydantic.constr(strip_whitespace=True)
FHIRRequiredString = pydantic.constr(min_length=1, strip_whitespace=True)

FHIRDateTime = exact_regex_constr(
    regex=r"([0-9]([0-9]([0-9][1-9]|[1-9]0)|[1-9]00)|[1-9]000)(-(0[1-9]|1[0-2])(-(0[1-9]|[1-2][0-9]|3[0-1])(T([01][0-9]|2[0-3]):[0-5][0-9]:([0-5][0-9]|60)(\.[0-9]+)?(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00)))?)?)?"
)
FHIRDate = exact_regex_constr(
    regex=r"([0-9]([0-9]([0-9][1-9]|[1-9]0)|[1-9]00)|[1-9]000)(-(0[1-9]|1[0-2])(-(0[1-9]|[1-2][0-9]|3[0-1]))?)?"
)
FHIRInstant = exact_regex_constr(
    regex=r"([0-9]([0-9]([0-9][1-9]|[1-9]0)|[1-9]00)|[1-9]000)-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])T([01][0-9]|2[0-3]):[0-5][0-9]:([0-5][0-9]|60)(\.[0-9]+)?(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))"
)
FHIRTime = exact_regex_constr(
    regex=r"([01][0-9]|2[0-3]):[0-5][0-9]:([0-5][0-9]|60)(\.[0-9]+)?"
)
FHIRCode = exact_regex_constr(regex=r"[^\s]+(\s[^\s]+)*")

FHIROid = exact_regex_constr(regex=r"urn:oid:[0-2](\.(0|[1-9][0-9]*))+")

FHIRId = exact_regex_constr(regex=r"[A-Za-z0-9\-\.]{1,64}")

FHIRBase64Binary = exact_regex_constr(regex=r"(\s*([0-9a-zA-Z\+/=]){4}\s*)+")

FHIRInt = pydantic.conint(strict=True)

FHIRUnsignedInt = pydantic.conint(strict=True, ge=0)

FHIRPositiveInt = pydantic.conint(strict=True, gt=0)


def validate_factory(cls):
    def validate_int_string(v):
        """Validate a string given a FHIR regex."""
        if isinstance(v, str):
            if re.match(exact_regex(cls.REGEX), v) is None:
                msg = f"String does not match {cls.__name__} pattern : {cls.REGEX}"
                raise ValueError(msg)
            return int(v)
        return v

    return validate_int_string


class FHIRInt(pydantic.conint(strict=True)):
    """Integer field following FHIR specs.

    https://www.hl7.org/fhir/datatypes.html#integer
    """

    REGEX = "[0]|[-+]?[1-9][0-9]*"

    @classmethod
    def __get_validators__(cls):
        yield validate_factory(cls)
        yield from super(FHIRInt, cls).__get_validators__()


class FHIRUnsignedInt(pydantic.conint(strict=True, ge=0)):
    """Unsigned integer field following FHIR specs.

    https://www.hl7.org/fhir/datatypes.html#unsignedInt
    """

    REGEX = "[0]|([1-9][0-9]*)"

    @classmethod
    def __get_validators__(cls):
        yield validate_factory(cls)
        yield from super(FHIRUnsignedInt, cls).__get_validators__()


class FHIRPositiveInt(pydantic.conint(strict=True, gt=0)):
    """Positive integer field following FHIR specs.

    Warning : FHIR Spec regex : "+?[1-9][0-9]*" seems invalid
              I think that intended use is "[+]?[1-9][0-9]*"

    https://www.hl7.org/fhir/datatypes.html#positiveInt
    """

    REGEX = "[+]?[1-9][0-9]*"

    @classmethod
    def __get_validators__(cls):
        yield validate_factory(cls)
        yield from super(FHIRPositiveInt, cls).__get_validators__()
