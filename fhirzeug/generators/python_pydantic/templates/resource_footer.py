def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


for subclass in inheritors(FHIRAbstractBase):
    subclass.update_forward_refs()


RESOURCE_TYPE_MAP: typing.Dict[str, Resource] = {}
for subclass in inheritors(Resource):
    RESOURCE_TYPE_MAP[subclass.__name__] = subclass


def from_dict(dict_: dict):
    """Factory to load resources directly.

    The resources will be instanciated based on their resourceType property."""

    try:
        if "resourceType" not in dict_:
            raise ValueError("Key 'resourceType' must be provided.")

        resource_type = dict_["resourceType"]
        if resource_type not in RESOURCE_TYPE_MAP:
            raise ValueError(f"ResourceType '{resource_type}' is not a valid Resource.")

        resource_class = RESOURCE_TYPE_MAP[resource_type]
        return resource_class(**dict_)

    except ValueError as e:
        # Raise a ValidationError if resourceType is not valid.
        # Works for both simple entity and nested entities.
        raise pydantic.ValidationError(
            model=FHIRAbstractResource,
            errors=[pydantic.error_wrappers.ErrorWrapper(exc=e, loc="resourceType")],
        )


def from_raw(*args, **kwargs):
    """Factory to load resources directly from the raw json string.

    The resources will be instanciated based on their resourceType property."""

    return from_dict(json_loads(*args, **kwargs))
