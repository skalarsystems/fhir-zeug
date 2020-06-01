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


def fhir_alias_generator(name: str) -> str:
    """Generator for pydantic aliases."""

    # 1) generate an alias if the member has a special name like class_
    if name.endswith("_"):
        return name[:-1]
    components = name.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])
