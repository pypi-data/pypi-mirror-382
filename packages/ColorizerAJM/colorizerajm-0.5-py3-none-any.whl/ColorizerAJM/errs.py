class InvalidColorCodeError(Exception):
    """Raised when an invalid color code is encountered."""
    ...


class MissingColorDefinitionError(Exception):
    """Raised when neither rgb nor hex is provided."""
    ...


class InvalidColorInputError(Exception):
    """Raised when invalid rgb or hex input is given."""
    ...
