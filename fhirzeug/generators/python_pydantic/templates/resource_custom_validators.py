# Define custom root validators.
# Validators are added to the already defined Resources in resource_footer.py .

import re  # noqa: F811
import typing
import pydantic


def _build_fhir_api_regex() -> re.Pattern:

    _all_resources_names = set()

    def _add_subresources(_resource: typing.Type[Resource]) -> None:
        _subresources = _resource.__subclasses__()
        if len(_subresources) == 0:
            _all_resources_names.add(_resource.__name__)
        else:
            for _subresource in _subresources:
                _add_subresources(_subresource)

    _add_subresources(Resource)
    _resources_to_ignore = {"MetadataResource", "Parameters"}
    for _resource_name in _resources_to_ignore:
        _all_resources_names.remove(_resource_name)

    resources_pattern = "|".join(sorted(_all_resources_names))

    return re.compile(
        # Taken from https://www.hl7.org/fhir/references.html#literal
        r"\A"
        # From https://www.hl7.org/fhir/http.html#root : "The protocols http: and https:
        # SHALL NOT be used to refer to different underlying objects" -> we do not take it
        # in base_url group.
        r"((http|https):\/\/(?P<base_url>([A-Za-z0-9\-\\\.\:\%\$]*\/)+))?"
        r"(?P<resource_type>(" + resources_pattern + r"))\/"
        r"(?P<resource_id>[A-Za-z0-9\-\.]{1,64})"
        r"(\/_history\/(?P<version>[A-Za-z0-9\-\.]{1,64}))?"
        r"\Z"
    )


_FHIR_API_REGEX = _build_fhir_api_regex()


class _ParsedLiteralReference(pydantic.BaseModel):
    """An object containing data parsed from a literal reference with known pattern."""

    base_url: typing.Optional[str] = None
    resource_type: str
    resource_id: str
    version: typing.Optional[str] = None

    @pydantic.validator("base_url")
    def base_url_to_none(cls, v: str) -> typing.Optional[str]:
        """Convert base_url to None if it's an empty url."""
        if not v:
            return None
        return v


def _parse_literal_reference(
    reference: typing.Optional[str],
) -> typing.Optional[_ParsedLiteralReference]:
    """Try to parse a reference as if the resource is server by a FHIR API server.

    Warnings :
        - not all literal references points to a FHIR Server.
        - if reference matches the patterns, it doesn't guarantee it points to a FHIR
          Server.
    """
    if reference is not None:
        match = _FHIR_API_REGEX.match(reference)
        if match is not None:
            return _ParsedLiteralReference(**match.groupdict())
    return None


class _AnyAbsoluteUrl(pydantic.BaseModel):
    """Validator used to test if a string is an absolute URL."""

    url: pydantic.AnyUrl


def _reference_validator(values):
    """Validate Reference resource values."""
    resource_type = values.get("type")
    reference = values.get("reference")
    if reference is not None:
        parsed_literal_reference = _parse_literal_reference(reference)
        if parsed_literal_reference is not None:
            if (
                resource_type is not None
                and parsed_literal_reference.resource_type != resource_type
            ):
                raise ValueError(
                    "Reference type and resource_type from reference URL must match."
                )
        elif reference.startswith("#"):
            # Reference is an internal fragment reference referring to contained resources.
            pass
        else:
            try:
                _AnyAbsoluteUrl(url=reference)
            except pydantic.ValidationError:
                # Reference is neither an absolute URL nor an URL relative to a FHIR
                # RESTful server with pattern "TYPE/ID".
                raise ValueError(
                    "Reference must be an absolute URL or an URL relative to a FHIR RESTful server"
                )
    return values
