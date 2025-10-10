from json import dump, load
from pathlib import Path

from . import _BaseColorizer


class CustomColorColorizer(_BaseColorizer):
    """
    CustomColorColorizer class for managing and handling custom color configurations.

    Attributes:
    DEFAULT_CUSTOM_COLOR_FILE_PATH: Default file path to store or load custom colors in JSON format.

    Methods:
    __init__: Initializes the CustomColorColorizer object. Sets up the custom color dictionary and file path, and optionally writes the custom colors during initialization.

    custom_colors (property): Retrieves and formats the custom colors dictionary. Processes raw input to ensure proper formatting and structure.

    custom_colors (setter): Sets the custom colors dictionary with formatted and processed data. Ensures consistency between different types of input values.

    write_custom_colors: Writes the current custom colors dictionary to a file at the specified file path in JSON format.

    read_custom_colors: Reads and loads the custom colors from a JSON file at the specified file path. Raises an AttributeError if the file path is invalid or does not have a .json extension.
    """
    DEFAULT_CUSTOM_COLOR_FILE_PATH = Path('./custom_colors.json')

    def __init__(self, custom_colors: dict = None, **kwargs):
        super().__init__(**kwargs)
        self._custom_colors = None
        self.custom_colors = custom_colors or {}
        self.custom_color_file_path = kwargs.get('custom_color_file_path',
                                                 self.__class__.DEFAULT_CUSTOM_COLOR_FILE_PATH)
        if kwargs.get('write_custom_colors_on_init', True):
            self.write_custom_colors()

    @property
    def custom_colors(self):
        """
        Retrieve and format custom colors based on predefined rules.
        If custom colors have not been populated yet,
        iterate over the internal dictionary of custom colors.
        If the value of a custom color is an integer,
        convert it to the corresponding color code.
        If the value is a string starting with '\033', leave it as is.
        Update the temporary dictionary with the formatted color data.
        Finally, set the internal custom colors to the processed dictionary
        and mark custom colors as populated.
        Return the custom colors dictionary.
        """
        return self._custom_colors

    @custom_colors.setter
    def custom_colors(self, value: dict):
        """
        Setter method for custom_colors property.

        This method updates the custom_colors dictionary with new color mappings provided in the 'value' parameter. Each key in the dictionary is converted to uppercase. The associated values must be in one of the following formats:
        - Integer: Treated as a color code and passed to the get_color_code method.
        - Tuple: Must contain three elements (RGB values), passed to the get_color_code method.
        - String: Must start with '\033', indicating an ANSI escape color code.

        Existing key-value pairs in custom_colors are retained unless overridden by new values with the same keys. The updated dictionary is then stored in the _custom_colors attribute.
        """
        temp_dict = {}
        if self._custom_colors:
            temp_dict = self._custom_colors.copy()
        for x in value.items():
            if isinstance(x[1], int):
                x = {x[0].upper(): self.get_color_code({x[0]: x[1]})}
            elif isinstance(x[1], tuple) and len(x[1]) == 3:
                x = {x[0].upper(): self.get_color_code(x[1])}
            elif isinstance(x[1], str) and x[1].startswith('\033'):
                x = {x[0].upper(): x[1]}
            temp_dict.update(x)
        self._custom_colors = temp_dict

    def write_custom_colors(self):
        """
        Writes the custom colors to a JSON file if custom colors are defined.

        The method checks if the `custom_colors` attribute is not empty. If present,
        it serializes the data using JSON and writes it to the file specified by
        `custom_color_file_path`. The output JSON file is formatted with an indentation
        of 4 spaces for readability.
        """
        if self.custom_colors:
            with open(self.custom_color_file_path, 'w') as f:
                dump(self.custom_colors, fp=f, indent=4)

    def read_custom_colors(self):
        """
        Reads custom colors from a JSON file specified by the custom_color_file_path attribute.

        If the file exists and has a .json extension, it reads the content, loads it as a dictionary of custom colors,
        and assigns it to the custom_colors attribute. A message is printed indicating the file from which the custom colors were loaded.

        Raises:
            AttributeError: If the custom_color_file_path does not point to a valid file or the file does not have a .json extension.
        """
        if self.custom_color_file_path.is_file() and self.custom_color_file_path.suffix == '.json':
            with open(self.custom_color_file_path, 'r') as f:
                self.custom_colors = load(f)
                print(f"custom colors loaded from {f.name}")
                # TODO: log here
        else:
            raise AttributeError(f"custom color file path is not a valid file or does not have a .json extension")
