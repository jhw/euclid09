from euclid09.cli.tags import Tags

import random
import unittest

class CLITagsTest(unittest.TestCase):

    def setUp(self):
        self.tracks = [{"name": "kick"}, {"name": "snare"}, {"name": "hihat"}]
        self.terms = {"drums": "percussion", "bass": "low-end", "melody": "tune"}
        self.tags = Tags(self.tracks, self.terms)

    def test_initialization(self):
        self.assertIsInstance(self.tags, dict)
        self.assertEqual(len(self.tags), len(self.tracks))
        for track in self.tracks:
            self.assertEqual(self.tags[track["name"]], track["name"])

    def test_validate_success(self):
        self.tags.terms = {track["name"]: "tag" for track in self.tracks}
        validated_tags = self.tags.validate()
        self.assertIs(validated_tags, self.tags)

    def test_randomise(self):
        random.seed(42)
        original_tags = self.tags.copy()
        self.tags.randomise()
        for key in self.tags:
            self.assertIn(self.tags[key], self.terms.keys())
            self.assertNotEqual(self.tags[key], original_tags[key])

    def test_randomise_repeatedly(self):
        for _ in range(10):
            self.tags.randomise()
            for key in self.tags:
                self.assertIn(self.tags[key], self.terms.keys())

if __name__ == "__main__":
    unittest.main()
