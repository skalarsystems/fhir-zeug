import pydantic


def exact_regex_constr(**kwargs):
    if kwargs.get("regex") is not None:
        kwargs["regex"] = r"\A" + kwargs["regex"].lstrip(r"\A").rstrip(r"\Z") + r"\Z"
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
