import enum
import typing
from collections.abc import Mapping

import pydantic


def choice_of_validator(choices, optional):
    def check_at_least_one(cls, values):

        setted_values = len(
            set(k for k, v in values.items() if v is not None) & choices
        )
        if setted_values > 1:
            raise ValueError(f"Only one of the fields is allowed to be set ({choices})")
        elif not optional and setted_values < 1:
            raise ValueError(f"A t least one of the fields needs to be set ({choices})")
        return values

    return check_at_least_one


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


class FHIRAbstractBase(pydantic.BaseModel):
    """Abstract base class for all FHIR elements.
    """

    def dict(self, *args, **kwargs):
        serialized = super().dict(*args, **kwargs)
        return _without_empty_items(serialized)

    class Config:
        alias_generator = camelcase_alias_generator
        allow_population_by_field_name = True


def _without_empty_items(obj: typing.Any):
    """
    Clean empty items: https://www.hl7.org/fhir/datatypes.html#representations
    TODO: add support for extensions: https://www.hl7.org/fhir/json.html#null
    """
    if isinstance(obj, Mapping):
        cleaned_dict = {}
        for key, value in obj.items():
            cleaned_value = _without_empty_items(value)
            if cleaned_value is not None:
                cleaned_dict[key] = cleaned_value

        if cleaned_dict:
            return cleaned_dict
        return None

    if isinstance(obj, str):
        if not obj:
            return None
        return obj

    if isinstance(obj, (list, tuple)):
        cleaned_list = []
        for item in obj:
            cleaned_item = _without_empty_items(item)
            if cleaned_item:
                cleaned_list.append(cleaned_item)

        if cleaned_list:
            return cleaned_list
        return None

    return obj
