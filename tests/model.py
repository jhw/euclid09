from euclid09.model import *

from unittest.mock import Mock, patch

import unittest

class ModelTest(unittest.TestCase):

    def setUp(self):
        self.pool = Mock()
        self.pool.match = Mock(return_value=[Mock(tag='sample') for _ in range(5)])
        self.tracks = [
            {"name": "kick",
             "machine": "sv.machines.beats.detroit.Detroit",
             "type": "sample",
             "temperature": 0.5,
             "density": 0.5},
            {"name": "clap",
             "machine": "sv.machines.beats.detroit.Detroit",
             "type": "sample",
             "temperature": 0.25,
             "density": 0.25}
        ]
        self.tag_mapping = {"kick": "sample",
                            "clap": "sample"}
        self.levels = {"kick": 1, "clap": 0.5}

        # Mock for SVSampleRef
        self.mock_sample = {
            "bank_name": "drums",
            "file_path": "kick.wav",
            "note": 36,
            "tags": ["kick"]
        }
        self.mock_samples = [SVSample(**self.mock_sample) for _ in range(2)]  # Create valid SVSampleRef instances

    def test_sample_track_creation(self):
        track = SampleTrack(**SampleTrack.randomise(self.pool, self.tracks[0], self.tag_mapping))
        self.assertIsInstance(track, SampleTrack)
        self.assertEqual(track.name, "kick")
        self.assertEqual(len(track.samples), 2)
        self.assertIn("mod", track.pattern)
        self.assertIn("fn", track.groove)

    def test_sample_track_clone(self):
        track = SampleTrack(**SampleTrack.randomise(self.pool, self.tracks[0], self.tag_mapping))
        track.samples = self.mock_samples  # Assign valid samples
        clone = track.clone()
        self.assertEqual(track.name, clone.name)
        self.assertEqual(track.samples, clone.samples)
        self.assertEqual(track.pattern, clone.pattern)
        self.assertEqual(track.groove, clone.groove)

    def test_sample_track_serialization(self):
        track = SampleTrack(**SampleTrack.randomise(self.pool, self.tracks[0], self.tag_mapping))
        track.samples = self.mock_samples  # Assign valid samples
        serialized = track.to_json()
        deserialized = SampleTrack.from_json(serialized)
        self.assertEqual(track.name, deserialized.name)
        self.assertEqual(track.pattern, deserialized.pattern)
        self.assertEqual(track.groove, deserialized.groove)

    def test_tracks_randomisation(self):
        tracks = Tracks.randomise(self.pool, self.tracks, self.tag_mapping)
        self.assertIsInstance(tracks, Tracks)
        self.assertEqual(len(tracks), len(self.tracks))
        clone = tracks.clone()
        self.assertEqual(len(clone), len(tracks))
        for t1, t2 in zip(tracks, clone):
            self.assertEqual(t1.name, t2.name)

    def test_tracks_serialization(self):
        tracks = Tracks.randomise(self.pool, self.tracks, self.tag_mapping)
        for track in tracks:
            track.samples = self.mock_samples  # Assign valid samples
        serialized = tracks.to_json()
        deserialized = Tracks.from_json(serialized)
        self.assertEqual(len(tracks), len(deserialized))
        for t1, t2 in zip(tracks, deserialized):
            self.assertEqual(t1.name, t2.name)

    def test_patch_creation(self):
        patch = Patch.randomise(self.pool, self.tracks, self.tag_mapping)
        for track in patch.tracks:
            track.samples = self.mock_samples  # Assign valid samples
        self.assertIsInstance(patch, Patch)
        clone = patch.clone()
        self.assertEqual(len(clone.tracks), len(patch.tracks))
        serialized = patch.to_json()
        deserialized = Patch.from_json(serialized)
        self.assertEqual(len(deserialized.tracks), len(patch.tracks))

    def test_patches_randomisation(self):
        patches = Patches.randomise(self.pool, self.tracks, self.tag_mapping, n=3)
        for patch in patches:
            for track in patch.tracks:
                track.samples = self.mock_samples  # Assign valid samples
        self.assertIsInstance(patches, Patches)
        self.assertEqual(len(patches), 3)
        clone = patches.clone()
        self.assertEqual(len(clone), len(patches))

    def test_patches_serialization(self):
        patches = Patches.randomise(self.pool, self.tracks, self.tag_mapping, n=3)
        for patch in patches:
            for track in patch.tracks:
                track.samples = self.mock_samples  # Assign valid samples
        serialized = patches.to_json()
        deserialized = Patches.from_json(serialized)
        self.assertEqual(len(deserialized), len(patches))
        for p1, p2 in zip(patches, deserialized):
            self.assertEqual(len(p1.tracks), len(p2.tracks))


if __name__ == "__main__":
    unittest.main()
