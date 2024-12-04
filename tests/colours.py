from euclid09.colours import Colour, Colours

from unittest.mock import patch

import unittest

class ColoursTest(unittest.TestCase):

    def test_colour_randomise_creates_valid_colour(self):
        colour = Colour.randomise()
        self.assertTrue(all(0 <= c <= 255 for c in colour))
        self.assertGreaterEqual(max(colour) - min(colour), 128)

    def test_colour_clone(self):
        original = Colour([100, 150, 200])
        clone = original.clone()
        self.assertEqual(original, clone)
        self.assertIsNot(original, clone)

    def test_colours_randomise_machines(self):
        tracks = [{"name": "kick"}, {"name": "snare"}, {"name": "hihat"}]
        machine_colours = Colours.randomise_machines(tracks)
        self.assertEqual(len(machine_colours), len(tracks))
        for colour in machine_colours.values():
            self.assertTrue(all(0 <= c <= 255 for c in colour))

    def test_colours_randomise_patches(self):
        patches = [{"id": i} for i in range(10)]
        patch_colours = Colours.randomise_patches(patches, quantise=2)
        self.assertEqual(len(patch_colours), len(patches))
        for i in range(len(patches)):
            self.assertNotEqual(patch_colours[i], patch_colours[i - 1] if i > 0 else None)

    def test_colours_randomise(self):
        tracks = [{"name": "track1"}, {"name": "track2"}]
        patches = [{"id": 1}, {"id": 2}, {"id": 3}]
        colours = Colours.randomise(tracks, patches)
        self.assertIn("machines", colours)
        self.assertIn("patches", colours)
        self.assertEqual(len(colours["machines"]), len(tracks))
        self.assertEqual(len(colours["patches"]), len(patches))

    def test_colour_randomise_raises_runtime_error(self):
        with patch("random.random", return_value=0): 
            with self.assertRaises(RuntimeError):
                Colour.randomise(offset=0, contrast=300, n=10)

if __name__ == "__main__":
    unittest.main()
