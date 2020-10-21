"""Test special cases for extension of JSON-primitive fields."""
import pytest
import typing

from fhirzeug.generators.python_pydantic.templates.resource_header import (
    FHIRAbstractBase,
    get_primitive_field_root_validator,
)
import pydantic


class ExampleModel(FHIRAbstractBase):
    """Model for tests that simulate the behavior of a generated resource."""

    field: typing.Optional[typing.List[typing.Optional[str]]]
    field__extension: typing.Optional[typing.List[typing.Optional[str]]]

    # Encountered once an issue with field names using "snake_case"
    # It is now tested for robustness
    snake_field: typing.Optional[typing.List[typing.Optional[str]]]
    snake_field__extension: typing.Optional[typing.List[typing.Optional[str]]]

    _validate_primitive_field = get_primitive_field_root_validator("field")
    _validate_primitive_snake_field = get_primitive_field_root_validator("snake_field")


class ContainerModel(FHIRAbstractBase):
    """Container model to test validation on submodels."""

    example: ExampleModel


@pytest.mark.parametrize(
    (
        "field_value",
        "field_extension_value",
        "field_validated_value",
        "field_extension_validated_value",
    ),
    [
        (["A"], ["extA"], ["A"], ["extA"]),
        (["A", None], None, ["A"], None),
        (["A", "B"], None, ["A", "B"], None),
        (["A", None], [None, "extB"], ["A", None], [None, "extB"]),
        (["A", "B"], [None, None], ["A", "B"], [None, None]),
    ],
)
@pytest.mark.parametrize("inversion", [True, False])
@pytest.mark.parametrize(
    ("field_name", "extension_name", "field_name_alias", "extension_name_alias"),
    [
        ("field", "field__extension", "field", "_field"),
        ("snake_field", "snake_field__extension", "snakeField", "_snakeField"),
    ],
)
def test_primitive_list_field(
    field_value: typing.Any,
    field_extension_value: typing.Any,
    field_validated_value: typing.Any,
    field_extension_validated_value: typing.Any,
    inversion: bool,
    field_name: str,
    extension_name: str,
    field_name_alias: str,
    extension_name_alias: str,
) -> None:
    """Test validation and export of fields containing a list of primitive values."""
    if inversion:
        # behavior must be symmetric
        field_value, field_extension_value = field_extension_value, field_value
        field_validated_value, field_extension_validated_value = (
            field_extension_validated_value,
            field_validated_value,
        )

    def _validate_example(example: ExampleModel) -> None:
        assert getattr(example, field_name) == field_validated_value
        assert getattr(example, extension_name) == field_extension_validated_value

        expected_dict = {}
        if field_validated_value is not None:
            expected_dict[field_name_alias] = field_validated_value
        if field_extension_validated_value is not None:
            expected_dict[extension_name_alias] = field_extension_validated_value
        assert example.dict(by_alias=True) == expected_dict

    example = ExampleModel(
        **{field_name: field_value, extension_name: field_extension_value}
    )
    _validate_example(example)

    _validate_example(
        ContainerModel(
            example={field_name: field_value, extension_name: field_extension_value}
        ).example
    )

    _validate_example(
        ContainerModel(
            example={
                field_name_alias: field_value,
                extension_name_alias: field_extension_value,
            }
        ).example
    )


@pytest.mark.parametrize(
    ("field_value", "field_extension_value",),
    [
        (["A", "B"], []),
        (["A", "B"], [None]),
        (["A", "B"], ["extA"]),
        (["A", "B"], ["extA", "extB", "extC"]),
        ([], []),
        ([None], [None]),
        (["A", None], ["extA", None]),
    ],
)
@pytest.mark.parametrize("inversion", [True, False])
@pytest.mark.parametrize(
    ("field_name", "extension_name", "field_name_alias", "extension_name_alias"),
    [
        ("field", "field__extension", "field", "_field"),
        ("snake_field", "snake_field__extension", "snakeField", "_snakeField"),
    ],
)
def test_primitive_list_field_must_fail(
    field_value: typing.Any,
    field_extension_value: typing.Any,
    inversion: bool,
    field_name: str,
    extension_name: str,
    field_name_alias: str,
    extension_name_alias: str,
) -> None:
    """Test model validation must fail."""
    if inversion:
        # behavior must be symmetric
        field_value, field_extension_value = field_extension_value, field_value

    with pytest.raises(pydantic.ValidationError):
        ExampleModel(**{field_name: field_value, extension_name: field_extension_value})

    with pytest.raises(pydantic.ValidationError):
        ContainerModel(
            example={field_name: field_value, extension_name: field_extension_value}
        )

    with pytest.raises(pydantic.ValidationError):
        ContainerModel(
            example={
                field_name_alias: field_value,
                extension_name_alias: field_extension_value,
            }
        )
