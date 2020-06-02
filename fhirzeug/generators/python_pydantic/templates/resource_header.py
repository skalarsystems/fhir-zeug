import typing
import enum
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

    class Config:
        alias_generator = camelcase_alias_generator
        allow_population_by_field_name = True
