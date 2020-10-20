import enum
import decimal
import stringcase
import typing
from collections.abc import Mapping
import json


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


def primitive_extension_validator(cls, v, values, field):
    """Validate the extension of a primitive field.

    Validator needs `values` in order to validate the extension against
    its primitive field value.

    Note: `primitive_field_name` and `primitive_field_value` refer to the
          primitive field that is extended and `field`/`v` refer to the
          extension field.

    Validators :
        - from https://www.hl7.org/fhir/json.html#primitive :
          "In the case where the primitive element may repeat, it is represented
          in two arrays. JSON null values are used to fill out both arrays so
          that the id and/or extension are aligned with the matching value in the
          first array."
          "Note: when one of the repeating elements has no value, it is represented
          in the first array using a null. When an element has a value but no
          extension/id, the second array will have a null at the position of that
          element."

        - TODO: validate cardinality ? Make optional initial field ?
    """
    primitive_field_name = primitive_extension_alias_generator(field.name)[1:]
    primitive_field_value = values.get(primitive_field_name)

    if v is not None and isinstance(v, list):
        if primitive_field_value is not None:
            # Primitive value is a list -> should already be validated by pydantic
            assert isinstance(primitive_field_value, list)

            # Validate that both lists have same length
            if len(primitive_field_value) != len(v):
                raise ValueError(
                    "When setting a primitive extension of a list, field list and field extension list must be both of same length."
                )
    return v


def camelcase_alias_generator(name: str) -> str:
    """Map snakecase to camelcase.

    This enables members to be created from camelCase. It takes the existing snakecase membername
    like foo_bar and converts it to its camelcase pendant fooBar.

    Additionally it removes trailing _, since this is used to make membernames of reserved keywords
    usable, like `class`.
    """
    if name.endswith("_"):
        name = name[:-1]
    return stringcase.camelcase(name)


def primitive_extension_alias_generator(name: str) -> str:
    """Map pydantic name to JSON extension name (only primitive fields).

    Add `_` prefix and remove `__extension` suffix.
    """
    extension_suffix = "__extension"
    if name.endswith(extension_suffix):
        return "_" + name[: -len(extension_suffix)]
    return name


def alias_generator(name: str) -> str:
    """Map a field name to its alias."""
    name = primitive_extension_alias_generator(name)
    name = camelcase_alias_generator(name)
    return name


class DocEnum(enum.Enum):
    """Enum with docstrings support."""

    def __new__(cls, value, doc=None):
        """Add docstring to the member of Enum if exists.

        Args:
            value: Enum member value
            doc: Enum member docstring, None if not exists
        """
        obj = str.__new__(cls, value)
        obj._value_ = value
        if doc:
            obj.__doc__ = doc
        return obj


class DecimalEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, Mapping):
            return (
                "{"
                + ", ".join(
                    f"{self.encode(k)}: {self.encode(v)}" for (k, v) in obj.items()
                )
                + "}"
            )
        if isinstance(obj, typing.Iterable) and (not isinstance(obj, str)):
            return "[" + ", ".join(map(self.encode, obj)) + "]"
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super().encode(obj)


def check_for_duplicate_keys(
    ordered_pairs: typing.List[typing.Tuple[typing.Hashable, typing.Any]]
) -> typing.Dict:
    """Check for duplicated keys.

    Raise ValueError if a duplicate key exists in provided ordered
    list of pairs, otherwise return a dict.

    Taken from https://stackoverflow.com/a/49518779/2750114 .
    """
    dict_out: typing.Dict = {}
    for key, val in ordered_pairs:
        if key in dict_out:
            raise ValueError(f"Duplicate key: {key}")
        else:
            dict_out[key] = val
    return dict_out


def json_dumps(*args, **kwargs):
    return json.dumps(*args, **kwargs, cls=DecimalEncoder)


def json_loads(*args, **kwargs):
    return json.loads(
        *args,
        **kwargs,
        parse_float=decimal.Decimal,
        object_pairs_hook=check_for_duplicate_keys,
    )


class FHIRAbstractBase(pydantic.BaseModel):
    """Abstract base class for all FHIR elements."""

    class Meta:
        profile: typing.List[str] = []
        """ Profiles this resource claims to conform to.
        List of `str` items. """

    def dict(self, *args, **kwargs):
        serialized = super().dict(*args, **kwargs)
        return _without_empty_items(serialized) or {}

    @pydantic.root_validator(pre=True)
    def strip_empty_items(cls, values: typing.Dict) -> typing.Dict:
        """This strips all empty elements according to the fhir spec."""
        return _without_empty_items(values) or {}

    @pydantic.root_validator()
    def dynamic_post_root_validator(cls, values: typing.Dict) -> typing.Dict:
        """Validate data.

        The behavior of this validator can be changed after definition of the BaseModel
        by using method `_add_post_root_validator`.
        """
        for validator in cls._dynamic_validators():
            values = validator(values)
        return values

    @classmethod
    def _add_post_root_validator(
        cls, validator: typing.Callable[[typing.Dict], typing.Dict]
    ) -> None:
        """Add a post root validator to the FHIR object.

        The order of the dynamic validators has not been a priority in this
        implementation. All dynamic validators must be considered to be independent
        from each other.
        TODO : add more flexibility to order validators.

        Internally, each FHIR class stores a list of dynamic validators. Then,
        `dynamic_post_root_validator` iterates over validators one by one using the
        __mro__ resolution order.

        Warning: there is currently no way of removing a validator. Since this
        method is more or less doing monkeypatching, it is preferred to use it
        carefully.
        """
        dynamic_validators_field = cls._get_dynamic_validators_field_name()
        dynamic_validators = getattr(cls, dynamic_validators_field, [])
        dynamic_validators.append(validator)
        setattr(cls, dynamic_validators_field, dynamic_validators)

    @classmethod
    def _dynamic_validators(
        cls,
    ) -> typing.Generator[typing.Callable[[typing.Dict], typing.Dict], None, None]:
        """Return a generator iterating over dynamic validators."""
        for subclass in cls.__mro__:
            if issubclass(subclass, FHIRAbstractBase):
                subclass_field = subclass._get_dynamic_validators_field_name()
                subclass_validators = getattr(subclass, subclass_field, None)
                if subclass_validators is not None:
                    yield from subclass_validators
            else:
                # If here, it means we are already in the parents' classes of FHIRAbstractBase
                # We do not need to continue to iterate
                return

    @classmethod
    def _get_dynamic_validators_field_name(cls) -> str:
        """Return a field "unique" to this class to store dynamic validators.

        Unicity is guaranted unless two FHIR classes has the same name and one is
        the child of the other one.
        TODO : ensure unicity of this field name in every cases.
        """
        return f"_dynamic_validators__{cls.__name__}"

    @pydantic.root_validator(pre=True)
    def validate_list_not_allowed_for_singleton_fields(cls, values):
        """Ensure that Singleton fields cannot receive a List as input.

        See issue on GitHub : https://github.com/skalarsystems/fhirzeug/issues/59

        This is also related to an issue on pydantic_repository :
        https://github.com/samuelcolvin/pydantic/issues/1268 .
        TODO: remove this validator once pydantic is updated to V2.
        """
        for cls_field in cls.__fields__.values():
            if cls_field.shape == pydantic.fields.SHAPE_SINGLETON:
                for field_name in [cls_field.alias, cls_field.name]:
                    if field_name in values:
                        if isinstance(values[field_name], list):
                            raise ValueError(
                                f"List is not suitable for a Singleton field : {field_name}."
                            )
        return values

    class Config:
        alias_generator = alias_generator
        allow_population_by_field_name = True
        extra = "forbid"
        json_dumps = json_dumps
        json_loads = json_loads


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
        cleaned_list_with_none = [_without_empty_items(item) for item in obj]
        cleaned_list = [item for item in cleaned_list_with_none if item is not None]
        if cleaned_list:
            return cleaned_list
        return None

    return obj
