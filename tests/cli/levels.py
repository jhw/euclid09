from euclid09.cli.levels import Levels

from collections import OrderedDict

import unittest

class CLILevelsTest(unittest.TestCase):

    def setUp(self):
        self.tracks = [{"name": "kick"}, {"name": "snare"}, {"name": "hihat"}]
        self.levels = Levels(self.tracks)

    def test_initialization(self):
        self.assertIsInstance(self.levels, OrderedDict)
        self.assertEqual(len(self.levels), len(self.tracks))
        for track in self.tracks:
            self.assertEqual(self.levels[track["name"]], 1)

    def test_solo(self):
        self.levels.solo("snare")
        for key in self.levels:
            expected_value = 1 if key == "snare" else 0
            self.assertEqual(self.levels[key], expected_value)

    def test_is_solo_property(self):
        self.assertFalse(self.levels.is_solo)
        self.levels.solo("kick")
        self.assertTrue(self.levels.is_solo)

    def test_solo_key_property(self):
        self.assertIsNone(self.levels.solo_key)
        self.levels.solo("hihat")
        self.assertEqual(self.levels.solo_key, "hih")

    def test_short_code_property(self):
        self.assertEqual(self.levels.short_code, "all")
        self.levels.solo("kick")
        self.assertEqual(self.levels.short_code, "kic")

    def test_solo_reset(self):
        self.levels.solo("kick")
        self.assertTrue(self.levels.is_solo)
        self.levels = Levels(self.tracks)
        self.assertFalse(self.levels.is_solo)
        self.assertEqual(self.levels.short_code, "all")

if __name__ == "__main__":
    pass
