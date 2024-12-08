
from euclid09.generators import *
from sv.algos.euclid import bjorklund

from unittest.mock import Mock, patch

import random
import unittest

class GeneratorTest(unittest.TestCase):
    
    def setUp(self):
        self.n_steps = 16
        self.rand = {"volume": random.Random(), "sound": random.Random(), "beat": random.Random(), "fx": random.Random()}
        self.dry_level = 0.8
        self.wet_level = 0.5
        self.temperature = 0.7
        self.density = 0.5

    def test_Beat_generator(self):
        groove_fn = Mock(return_value=0.8)
        pattern_fn = bjorklund(steps=16, pulses=4)
        mock_self = Mock()
        mock_self.note = Mock(return_value="trig_block")
        beat_generator = Beat(
            mock_self, self.n_steps, self.rand, pattern=pattern_fn, groove=groove_fn, 
            temperature=self.temperature, density=self.density, dry_level=self.dry_level, bpm = 120, tpb = 1
        )
        output = list(beat_generator)
        for i, trig_block in output:
            self.assertIn(i, range(self.n_steps))
            self.assertEqual(trig_block, "trig_block")
        self.assertTrue(len(output) <= self.n_steps)

    def test_GhostEcho_generator(self):
        mock_self = Mock()
        mock_self.modulation = Mock(return_value="echo_trig_block")
        echo_generator = GhostEcho(
            mock_self, self.n_steps, self.rand, wet_level=self.wet_level, quantise=4, bpm = 120, tpb = 1
        )
        output = list(echo_generator)
        for i, trig_block in output:
            self.assertIn(i, range(self.n_steps))
            self.assertEqual(trig_block, "echo_trig_block")
            self.assertEqual(i % 4, 0)
        self.assertTrue(len(output) <= self.n_steps // 4)

if __name__ == "__main__":
    unittest.main()
