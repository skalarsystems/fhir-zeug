import enum
import decimal
import stringcase
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
            raise ValueError(f"At least one of the fields needs to be set ({choices})")
        return values

    return check_at_least_one


def camelcase_alias_generator(name: str) -> str:
    """Maps snakecase to camelcase.

    This enables members to be created from camelCase. It takes the existing snakecase membername
    like foo_bar and converts it to its camelcase pendant fooBar.

    Additionally it removes trailing _, since this is used to make membernames of reserved keywords
    usable, like `class`.
    """

    if name.endswith("_"):
        name = name[:-1]
    return stringcase.camelcase(name)


class DocEnum(enum.Enum):
    """Enum with docstrings support"""

    def __new__(cls, value, doc=None):
        """add docstring to the member of Enum if exists

        Args:
            value: Enum member value
            doc: Enum member docstring, None if not exists
        """
        obj = str.__new__(cls, value)
        obj._value_ = value
        if doc:
            obj.__doc__ = doc
        return obj


def decimal_to_json(value: decimal.Decimal) -> typing.Union[float, int]:
    """Convert a decimal to float or int, depending on if it has a decimal part.

    It is for JSON serialization - to serialize it in the same form as was
    originally provided.
    """
    if value.as_tuple().exponent == 0:
        return int(value)
    return float(value)


class FHIRAbstractBase(pydantic.BaseModel):
    """Abstract base class for all FHIR elements.
    """

    class Meta:
        profile: typing.List[str] = []
        """ Profiles this resource claims to conform to.
        List of `str` items. """

    def dict(self, *args, **kwargs):
        serialized = super().dict(*args, **kwargs)
        return _without_empty_items(serialized)

    @pydantic.root_validator(pre=True)
    def strip_empty_items(cls, valuse):
        """This strips all empty elements according to the fhir spec."""
        return _without_empty_items(valuse) or {}

    class Config:
        alias_generator = camelcase_alias_generator
        allow_population_by_field_name = True
        json_encoders = {
            # Pydantic by default converts decimals to floats in JSON output
            # (adding `.0` for integer). We prefer to leave them in the original
            # form.
            decimal.Decimal: decimal_to_json
        }


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
        obj = obj.strip()
        if not obj:
            return None
        return obj

    if isinstance(obj, (list, tuple)):
        cleaned_list = [_without_empty_items(item) for item in obj]
        if cleaned_list:
            return cleaned_list
        return None

    return obj
