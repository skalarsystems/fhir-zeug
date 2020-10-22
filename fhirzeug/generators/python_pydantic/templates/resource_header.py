import enum
import decimal
import stringcase
import typing
from collections.abc import Mapping
import json


import pydantic


_EXTENSION_SUFFIX = "__extension"


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


def get_primitive_field_root_validator(field_name: str) -> classmethod:
    """Build a root validator that validates a primitive field.

    Root validator is used in order to have access to all other (already validated)
    fields. `skip_on_failure` is set in order to avoid validating fields that
    might not be cleaned.
    """

    @pydantic.root_validator(pre=True, skip_on_failure=True, allow_reuse=True)
    def _validator(
        cls, values: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        # Check if both field and extension are set.
        # If field or extension is not set, we do not need to validate the consistency
        # between them.
        # Note: that might not be the case anymore when we will also validate cardinality.

        # Field can either be present as the real field name or its alias
        inner_field_name = field_name
        if inner_field_name not in values:
            inner_field_name = alias_generator(inner_field_name)
            if inner_field_name not in values:
                return values

        # Extension can either be present as the real extension name or its alias
        extension_name = field_name + _EXTENSION_SUFFIX
        if extension_name not in values:
            extension_name = alias_generator(extension_name)
            if extension_name not in values:
                return values

        # Get field and extension values
        field_value = values[inner_field_name]
        extension_value = values[extension_name]

        # Validate them and get validated values
        validated_field_value, validated_extension_value = _validate_primitive_field(
            field_value, extension_value
        )

        # Assign new values and return
        values[inner_field_name] = validated_field_value
        values[extension_name] = validated_extension_value
        return values

    return _validator


def _validate_primitive_field(
    initial_field_value: typing.Any, extension_field_value: typing.Any
) -> typing.Tuple[typing.Any, typing.Any]:
    """Validate the consistency of a primitive field or list-of-primitives field.

    Note: `initial_field_value` refer to the primitive field that is extended
          and `extension_field_value` refer to the extension field.

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

        - TODO: validate cardinality ? Make initial field optional ?

    See tests in `tests/pydantic/test_primitive_list.py` for examples.
    """
    if isinstance(extension_field_value, list):
        if initial_field_value is None:
            if None in extension_field_value:
                # Should never reach this point.
                raise Exception(
                    "None values must have already been removed by `_without_empty_items`."
                )
        else:
            # Extension is a list -> initial field must also be a list (or None)
            if not isinstance(initial_field_value, list):
                raise ValueError(
                    f"If an extension of a primitive field is a list, the initial field must be either `null` or a list. Not {type(initial_field_value)}."
                )

            # Validate that both lists have same length
            if len(initial_field_value) != len(extension_field_value):
                if all(value is None for value in initial_field_value) and any(
                    value is not None for value in extension_field_value
                ):
                    # Case `initial_field_value=[None]` and `extension_field_value=['A', None, 'B']`
                    # Initial value is set to `None` and `None` values in second array are removed.
                    return (
                        None,
                        [value for value in extension_field_value if value is not None],
                    )
                elif any(value is not None for value in initial_field_value) and all(
                    value is None for value in extension_field_value
                ):
                    # Case `initial_field_value=['A', None, 'B']` and `extension_field_value=[None]`
                    # Extension value is set to `None` and `None` values in first array are removed.
                    return (
                        [value for value in initial_field_value if value is not None],
                        None,
                    )
                else:
                    raise ValueError(
                        "When setting a primitive extension of a list, field list and field extension list must be both of same length."
                    )

            if len(initial_field_value) == 0:
                raise ValueError(
                    "When setting a primitive extension of a list, field and field extension cannot be both set with an empty list."
                )

            for initial_item, extension_item in zip(
                initial_field_value, extension_field_value
            ):
                if initial_item is None and extension_item is None:
                    raise ValueError(
                        "When setting a primitive extension of a list, field item and primitive item cannot be `null` at the same position."
                    )

    if isinstance(initial_field_value, list):
        if extension_field_value is None:
            # Should never reach this point.
            # List is not extended. Therefore, `null` values must not be present.
            # `null` values should have already been removed by `_without_empty_items` since
            # there wasn't an extension list.
            if None in initial_field_value:
                raise Exception(
                    "None values must have already been removed by `_without_empty_items`."
                )
        elif isinstance(extension_field_value, list):
            # Case already handled above
            pass
        else:
            # Should have already been validated.
            raise ValueError(
                "Extension of a field with a list of primitive type must be of type `list`."
            )

    return initial_field_value, extension_field_value


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
    if name.endswith(_EXTENSION_SUFFIX):
        return "_" + name[: -len(_EXTENSION_SUFFIX)]
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
    """Clean empty items.

    See : https://www.hl7.org/fhir/datatypes.html#representations

    Extension of list of primitive values is handled differently by
    its own root validator. See: https://www.hl7.org/fhir/json.html#null
    """
    if isinstance(obj, Mapping):
        cleaned_dict = {}
        for key, value in obj.items():
            primitive_key, extension_key = None, None
            if key.startswith("_") and key[1:] in obj:
                primitive_key = key[1:]
                extension_key = key
            elif ("_" + key) in obj:
                primitive_key = key
                extension_key = "_" + key
            elif (
                key.endswith(_EXTENSION_SUFFIX)
                and key[: -len(_EXTENSION_SUFFIX)] in obj
            ):
                primitive_key = key[: -len(_EXTENSION_SUFFIX)]
                extension_key = key
            elif key + _EXTENSION_SUFFIX in obj:
                primitive_key = key
                extension_key = key + _EXTENSION_SUFFIX

            if (primitive_key, extension_key) != (None, None):
                primitive_value = obj[primitive_key]
                extension_value = obj[extension_key]
                if isinstance(primitive_value, list) and isinstance(
                    extension_value, list
                ):
                    if primitive_key not in cleaned_dict:
                        assert extension_key not in cleaned_dict
                        # WARNING : Here lists consistency is NOT validated
                        #           This is done later by the primitive field validator
                        cleaned_dict[primitive_key] = [
                            _without_empty_items(value) for value in primitive_value
                        ]
                        cleaned_dict[extension_key] = [
                            _without_empty_items(value) for value in extension_value
                        ]
                    continue

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
