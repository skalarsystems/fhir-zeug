from collections.abc import Mapping


def camelcase_alias_generator(name: str) -> str:
    """Maps snakecase to camelcase.
    
    This enables members to be created from camelCase. It takes the existing camelcase membername
    like foo_bar and converts it to its camelcase pedant fooBar.
    
    Additionally it removes trailing _, since this is used to make membernames of reserved keywords
    usable, like `class`.
    """

    if name.endswith("_"):
        return name[:-1]

    components = name.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])


def _without_empty_items(obj: typing.Any):
    """
    Clean empty items: https://www.hl7.org/fhir/datatypes.html#representations
    TODO: add support for extensions: https://www.hl7.org/fhir/json.html#null
    """
    if isinstance(obj, Mapping):
        cleaned = {}
        for key, value in obj.items():
            cleaned_value = _without_empty_items(value)
            if cleaned_value is not None:
                cleaned[key] = cleaned_value
        if cleaned:
            return cleaned
        return None
    if isinstance(obj, str):
        if not obj:
            return None
        return obj

    if isinstance(obj, (list, tuple)):
        cleaned = [_without_empty_items(item) for item in obj]
        if any((item is not None for item in cleaned)):
            return cleaned
        return None

    return obj


class FHIRAbstractBase(pydantic.BaseModel):
    """Abstract base class for all FHIR elements.
    """

    class Config:
        alias_generator = camelcase_alias_generator
        allow_population_by_field_name = True

    # def dict(self, *args, **kwargs):
    #     serialized = super().dict(*args, **kwargs)
    #     return _without_empty_items(serialized)
