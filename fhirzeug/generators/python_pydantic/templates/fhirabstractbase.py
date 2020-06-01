from collections.abc import Mapping


class FHIRValidationError(Exception):
    """ Exception raised when one or more errors occurred during model
    validation.
    """

    def __init__(self, errors, path=None):
        """ Initializer.
        
        :param errors: List of Exception instances. Also accepts a string,
            which is converted to a TypeError.
        :param str path: The property path on the object where errors occurred
        """
        if not isinstance(errors, list):
            errors = [TypeError(errors)]
        msgs = "\n  ".join([str(e).replace("\n", "\n  ") for e in errors])
        message = "{}:\n  {}".format(path or "{root}", msgs)

        super(FHIRValidationError, self).__init__(message)

        self.errors = errors
        """ A list of validation errors encountered. Typically contains
        TypeError, KeyError, possibly AttributeError and others. """

        self.path = path
        """ The path on the object where the errors occurred. """

    def prefixed(self, path_prefix):
        """ Creates a new instance of the receiver, with the given path prefix
        applied. """
        path = (
            "{}.{}".format(path_prefix, self.path)
            if self.path is not None
            else path_prefix
        )
        return self.__class__(self.errors, path)


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

    # def dict(self, *args, **kwargs):
    #     serialized = super().dict(*args, **kwargs)
    #     return _without_empty_items(serialized)
