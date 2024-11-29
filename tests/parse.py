from euclid09.parse import *

from unittest.mock import Mock

import unittest

class ParseTest(unittest.TestCase):

    def test_is_abbrev(self):
        self.assertTrue(is_abbrev("ny", "New York"))
        self.assertFalse(is_abbrev("bx", "New York"))
        self.assertTrue(is_abbrev("N", "New York"))
        self.assertFalse(is_abbrev("LAX", "Los Angeles"))

    def test_matches_number(self):
        self.assertTrue(matches_number("123"))
        self.assertTrue(matches_number("123.456"))
        self.assertFalse(matches_number("abc"))

    def test_matches_int(self):
        self.assertTrue(matches_int("123"))
        self.assertTrue(matches_int("-123"))
        self.assertFalse(matches_int("123.456"))
        self.assertFalse(matches_int("abc"))

    def test_matches_float(self):
        self.assertTrue(matches_float("123.456"))
        self.assertFalse(matches_float("123"))
        self.assertFalse(matches_float("abc"))

    def test_matches_enum(self):
        options = ["primary", "secondary", "success"]
        self.assertTrue(matches_enum("primary", options=options))
        self.assertTrue(matches_enum("pri", options=options))  # Test abbreviation
        self.assertFalse(matches_enum("warning", options=options))

    def test_parse_number(self):
        self.assertEqual(parse_number("123"), 123)
        self.assertEqual(parse_number("123.456"), 123.456)

    def test_parse_int(self):
        self.assertEqual(parse_int("123"), 123)
        self.assertEqual(parse_int("-123"), -123)

    def test_parse_float(self):
        self.assertEqual(parse_float("123.456"), 123.456)

    def test_parse_str(self):
        self.assertEqual(parse_str("test string"), "test string")

    def test_parse_enum(self):
        options = ["primary", "secondary", "success"]
        self.assertEqual(parse_enum("primary", options=options), "primary")
        self.assertEqual(parse_enum("pri", options=options), "primary")
        with self.assertRaises(RuntimeError):
            parse_enum("invalid", options=options)

    def test_parse_line_decorator(self):
        @parse_line([{"name": "n", "type": "int"}])
        def sample_function(self, n):
            return n
        instance = Mock()
        self.assertEqual(sample_function(instance, "5"), 5)
        with self.assertLogs(level="ERROR") as log:
            sample_function(instance, "invalid")
            self.assertIn("n is invalid", log.output[0])
        with self.assertLogs(level="ERROR") as log:
            sample_function(instance, "")
            self.assertIn("Please enter n", log.output[0])

if __name__ == "__main__":
    unittest.main()
