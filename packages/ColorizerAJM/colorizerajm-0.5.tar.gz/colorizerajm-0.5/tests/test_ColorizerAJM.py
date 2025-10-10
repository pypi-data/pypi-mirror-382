import unittest

from ColorizerAJM import Colorizer


class TestColorizer(unittest.TestCase):

    def setUp(self):
        self.colorizer = Colorizer()

    @classmethod
    def tearDownClass(cls):
        if Colorizer.DEFAULT_CUSTOM_COLOR_FILE_PATH.is_file():
            Colorizer.DEFAULT_CUSTOM_COLOR_FILE_PATH.unlink()

    def test_colorize(self):
        colored_text = self.colorizer.colorize('Hello World', 'RED')
        self.assertTrue(colored_text.startswith(self.colorizer.DEFAULT_COLOR_CODES['RED']))

    def test_custom_colors(self):
        self.colorizer = Colorizer(custom_colors={'MY_COLOR': 123})
        self.assertEqual(self.colorizer.custom_colors, {'MY_COLOR': '\x1b[38;5;123m'})

    def test_all_loaded_colors(self):
        self.assertIsNotNone(self.colorizer.all_loaded_colors)

    def test_random_color(self):
        color = Colorizer.random_color()
        self.assertTrue(color.startswith(self.colorizer.CUSTOM_COLOR_PREFIX))

    def test_print_color(self):
        self.assertIsNone(self.colorizer.print_color('Test', color='BLUE'))

    def test_preview_color_id(self):
        self.assertIsNone(self.colorizer.preview_color_id(50))

    def test_print_color_table(self):
        self.assertIsNone(self.colorizer.print_color_table(10))

    def test_stringify_color_id(self):
        s = Colorizer.stringify_color_id((255, 255, 255))
        self.assertEqual(s, "\x1b[38;2;255;255;255m")

    def test__parse_color_string(self):
        s = self.colorizer._parse_color_string('RED')
        self.assertEqual(s, self.colorizer.DEFAULT_COLOR_CODES['RED'])

    def test_get_color_code(self):
        code = self.colorizer.get_color_code('RED')
        self.assertEqual(code, self.colorizer.DEFAULT_COLOR_CODES['RED'])

    def test_make_bold(self):
        bold_code = Colorizer.make_bold(self.colorizer.DEFAULT_COLOR_CODES['RED'])
        self.assertEqual(bold_code, self.colorizer.DEFAULT_COLOR_CODES['RED'].replace('[', '[1;'))


if __name__ == '__main__':
    unittest.main()
