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


class FHIRAbstractBase(pydantic.BaseModel):
    """Abstract base class for all FHIR elements.
    """

    class Config:
        alias_generator = camelcase_alias_generator
        allow_population_by_field_name = True
