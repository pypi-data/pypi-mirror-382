from . import errs
from abc import abstractmethod
from typing import Union, Tuple


class _ColorizerBasicAttrs:
    """
    Represents a collection of basic attributes and constants for defining and handling color codes.

    Attributes:
    RED: String representing the color name 'RED'.
    GREEN: String representing the color name 'GREEN'.
    BLUE: String representing the color name 'BLUE'.
    YELLOW: String representing the color name 'YELLOW'.
    MAGENTA: String representing the color name 'MAGENTA'.
    CYAN: String representing the color name 'CYAN'.
    WHITE: String representing the color name 'WHITE'.
    GRAY: String representing the color name 'GRAY'.
    LIGHT_GRAY: String representing the color name 'LIGHT_GRAY'.
    BLACK: String representing the color name 'BLACK'.

    DEFAULT_COLOR_CODES: Dictionary mapping basic color names to their respective ANSI escape color codes.

    RESET_COLOR_CODE: String representing the reset code to clear any applied color formatting.
    CUSTOM_COLOR_PREFIX: ANSI escape sequence prefix for custom indexed colors.
    RGBA_COLOR_PREFIX: ANSI escape sequence prefix for RGBA-based color codes.
    COLOR_SUFFIX: Suffix indicating the end of an ANSI color escape sequence.
    ALL_VALID_CODES_RANGE: Range representing all valid custom color code values (0-255).
    """
    RED = 'RED'
    GREEN = 'GREEN'
    BLUE = 'BLUE'
    YELLOW = 'YELLOW'
    MAGENTA = 'MAGENTA'
    CYAN = 'CYAN'
    WHITE = 'WHITE'
    GRAY = 'GRAY'
    LIGHT_GRAY = 'LIGHT_GRAY'
    BLACK = 'BLACK'

    DEFAULT_COLOR_CODES = {
        RED: '\033[91m',
        GREEN: '\033[92m',
        BLUE: '\033[94m',
        YELLOW: '\033[93m',
        MAGENTA: '\033[95m',
        CYAN: '\033[96m',
        WHITE: '\033[97m',
        GRAY: '\x1b[90m',
        LIGHT_GRAY: '\x1b[37m',
        BLACK: '\x1b[30m'
    }

    RESET_COLOR_CODE = '\033[0m'
    CUSTOM_COLOR_PREFIX = '\033[38;5;'
    RGBA_COLOR_PREFIX = '\033[38;2;'
    COLOR_SUFFIX = 'm'
    ALL_VALID_CODES_RANGE = range(0, 256)


class _BaseColorizer(_ColorizerBasicAttrs):
    """
    _BaseColorizer class is a base class for handling colorization logic, extending _ColorizerBasicAttrs. It includes methods for parsing, validating, and managing color codes and custom colors.

    __init__(self, **kwargs)
        Constructor for the _BaseColorizer class.
        Parameters:
            kwargs: Additional arguments to configure the instance.
                - 'ignore_invalid_colors' (bool): Flag to ignore invalid color codes when True. Defaults to False.

    @property custom_colors
        Abstract property that must be implemented in subclasses.
        Represents the dictionary containing custom color definitions.

    @staticmethod stringify_color_id(color_id: Union[int, tuple])
        Converts a color ID (an integer or RGB tuple) into a string format for color codes.
        Parameters:
            color_id: The input color ID, either an integer (0-255) or an RGB tuple of three integers (0-255 each).
        Returns:
            A formatted ANSI escape code string for the given color.
        Raises:
            InvalidColorCodeError: If color_id is not a valid integer or RGB tuple.

    _parse_color_string(self, color_string: str)
        Parses the input color string and retrieves the corresponding color code.
        Parameters:
            color_string: The color as a textual string.
        Returns:
            A string containing the ANSI escape code if the color is valid. If invalid and 'ignore_invalid_colors' is False, raises an exception.
        Raises:
            InvalidColorCodeError: If the input color string is invalid and 'ignore_invalid_colors' is not set.

    get_color_code(self, color: Union[str, dict, int, Tuple[int, int, int]]) -> str
        Retrieves the color code based on the provided input, which can be a string, dictionary, integer, or RGB tuple.
        Parameters:
            color: The input representing a color. It can be:
                - str: A color string.
                - dict: A dictionary containing a color name and its ID.
                - int: An integer representing a color ID.
                - tuple: An RGB tuple of three integers.
        Returns:
            A string containing the ANSI escape code for the provided color.
        Raises:
            InvalidColorCodeError: If the input color cannot be validated or processed.
            AttributeError: If the input type is not supported (not str, dict, int, or tuple).
    """
    def __init__(self, **kwargs):
        self.ignore_invalid_colors = kwargs.get('ignore_invalid_colors', False)

    @property
    @abstractmethod
    def custom_colors(self):
        ...

    @staticmethod
    def stringify_color_id(color_id: Union[int, tuple]):
        """ Converts a color ID (integer or RGB tuple) into a string format for colorization.
            - For an integer within the valid range (0-255), returns the ANSI escape code for the color.
            - For a tuple of 3 integers (each in the range 0-255), returns the RGB ANSI escape code.
            Raises:
                InvalidColorCodeError: If the input is not a valid color ID. """
        if isinstance(color_id, int):
            if color_id in _BaseColorizer.ALL_VALID_CODES_RANGE:
                return f'{_BaseColorizer.CUSTOM_COLOR_PREFIX}{color_id}{_BaseColorizer.COLOR_SUFFIX}'
            else:
                raise errs.InvalidColorCodeError("color_id must be an integer between 0 and 255")
        elif isinstance(color_id, tuple):
            if len(color_id) == 3 and all(c in _BaseColorizer.ALL_VALID_CODES_RANGE for c in color_id):
                return f'{_BaseColorizer.RGBA_COLOR_PREFIX}{color_id[0]};{color_id[1]};{color_id[2]}{_BaseColorizer.COLOR_SUFFIX}'
            raise errs.InvalidColorCodeError()

    def _parse_color_string(self, color_string: str):
        """
        Parses a color string and returns the corresponding color code.
        If the color string is not found in the default color codes dictionary or the custom colors dictionary,
        it returns an empty string.
        If the 'ignore_invalid_colors' flag is not set, it raises an InvalidColorCodeError exception.
        """
        full_str = _BaseColorizer.DEFAULT_COLOR_CODES.get(color_string.upper(),
                                                          self.custom_colors.get(color_string.upper(), ''))
        if full_str != '':
            return full_str
        else:
            if not self.ignore_invalid_colors:
                raise errs.InvalidColorCodeError('given color did not match any of the available colors')
            return full_str

    def get_color_code(self, color: Union[str, dict, int, Tuple[int, int, int]]) -> str:
        """
        A method to retrieve color code based on the input provided.
        The input can be a string, dictionary, or integer representing the color.
        If a dictionary is provided, it extracts the color and color ID and returns the color code.
        If an integer is provided, it converts it to color code using the color ID.
        For a string, it parses the color string and returns the corresponding color code.
        If the input is not of type str, dict, or int, it raises an AttributeError.
        """
        if isinstance(color, dict):
            color, color_id = [x for x in color.items()][0] if color else [None, None]
            return self.stringify_color_id(color_id)
        elif isinstance(color, int):
            color_id = color
            return self.get_color_code(self.stringify_color_id(color_id))
        elif isinstance(color, tuple):
            return self.stringify_color_id(color)
        elif isinstance(color, str):
            return self._parse_color_string(color)
        else:
            raise AttributeError(f"color attribute must be a string or a dictionary, not {type(color).__name__}")