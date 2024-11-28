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
        self.tag_mapping = {"kick": "sample", "clap": "sample"}
        self.sample_cutoff  = 0.5
        self.levels = {"kick": 1, "clap": 0.5}

        # Mock for SVSampleRef
        self.mock_sample = {
            "bank_name": "drums",
            "file_path": "kick.wav",
            "note": 36,
            "tags": ["kick"]
        }
        self.mock_samples = [SVSample(**self.mock_sample) for _ in range(2)]

    def test_sample_track_creation(self):
        track = SampleTrack.randomise(track = self.tracks[0],
                                      pool = self.pool,
                                      tags = self.tag_mapping,
                                      sample_cutoff = self.sample_cutoff)
        self.assertIsInstance(track, SampleTrack)
        self.assertEqual(track.name, "kick")
        self.assertEqual(len(track.samples), 2)
        self.assertIn("mod", track.pattern)
        self.assertIn("fn", track.groove)

    def test_sample_track_clone(self):
        track = SampleTrack.randomise(track = self.tracks[0],
                                      pool = self.pool,
                                      tags = self.tag_mapping,
                                      sample_cutoff = self.sample_cutoff)
        track.samples = self.mock_samples
        clone = track.clone()
        self.assertEqual(track.name, clone.name)
        self.assertEqual(track.samples, clone.samples)
        self.assertEqual(track.pattern, clone.pattern)
        self.assertEqual(track.groove, clone.groove)

    def test_sample_track_serialization(self):
        track = SampleTrack.randomise(track = self.tracks[0],
                                      pool = self.pool,
                                      tags = self.tag_mapping,
                                      sample_cutoff = self.sample_cutoff)
        track.samples = self.mock_samples
        serialized = track.to_json()
        deserialized = SampleTrack.from_json(serialized)
        self.assertEqual(track.name, deserialized.name)
        self.assertEqual(track.pattern, deserialized.pattern)
        self.assertEqual(track.groove, deserialized.groove)

    def test_tracks_randomisation(self):
        tracks = Tracks.randomise(tracks = self.tracks,
                                  pool = self.pool,
                                  tags = self.tag_mapping,
                                  sample_cutoff = self.sample_cutoff)
        self.assertIsInstance(tracks, Tracks)
        self.assertEqual(len(tracks), len(self.tracks))
        clone = tracks.clone()
        self.assertEqual(len(clone), len(tracks))
        for t1, t2 in zip(tracks, clone):
            self.assertEqual(t1.name, t2.name)

    def test_tracks_serialization(self):
        tracks = Tracks.randomise(tracks = self.tracks,
                                  pool = self.pool,
                                  tags = self.tag_mapping,
                                  sample_cutoff = self.sample_cutoff)
        for track in tracks:
            track.samples = self.mock_samples
        serialized = tracks.to_json()
        deserialized = Tracks.from_json(serialized)
        self.assertEqual(len(tracks), len(deserialized))
        for t1, t2 in zip(tracks, deserialized):
            self.assertEqual(t1.name, t2.name)

    def test_patch_creation(self):
        patch = Patch.randomise(tracks = self.tracks,
                                pool = self.pool,
                                tags = self.tag_mapping,
                                sample_cutoff = self.sample_cutoff)
        for track in patch.tracks:
            track.samples = self.mock_samples
        self.assertIsInstance(patch, Patch)
        clone = patch.clone()
        self.assertEqual(len(clone.tracks), len(patch.tracks))
        serialized = patch.to_json()
        deserialized = Patch.from_json(serialized)
        self.assertEqual(len(deserialized.tracks), len(patch.tracks))

    def test_patches_randomisation(self):
        patches = Patches.randomise(tracks = self.tracks,
                                    pool = self.pool,
                                    tags = self.tag_mapping,
                                    sample_cutoff = self.sample_cutoff,
                                    n = 3)
        for patch in patches:
            for track in patch.tracks:
                track.samples = self.mock_samples
        self.assertIsInstance(patches, Patches)
        self.assertEqual(len(patches), 3)
        clone = patches.clone()
        self.assertEqual(len(clone), len(patches))

    def test_patches_serialization(self):
        patches = Patches.randomise(tracks = self.tracks,
                                    pool = self.pool,
                                    tags = self.tag_mapping,
                                    sample_cutoff = self.sample_cutoff,
                                    n = 3)
        for patch in patches:
            for track in patch.tracks:
                track.samples = self.mock_samples
        serialized = patches.to_json()
        deserialized = Patches.from_json(serialized)
        self.assertEqual(len(deserialized), len(patches))
        for p1, p2 in zip(patches, deserialized):
            self.assertEqual(len(p1.tracks), len(p2.tracks))

    # New Tests
    def test_mutation_tracks(self):
        tracks = Tracks.randomise(tracks = self.tracks,
                                  pool = self.pool,
                                  tags = self.tag_mapping,
                                  sample_cutoff = self.sample_cutoff)
        for track in tracks:
            track.samples = self.mock_samples
        tracks.mutate_attr("temperature", limit=0.1)
        for track in tracks:
            self.assertGreaterEqual(track.temperature, 0.1)
            self.assertLessEqual(track.temperature, 0.9)

    def test_mutation_patch(self):
        patch = Patch.randomise(tracks = self.tracks,
                                pool = self.pool,
                                tags = self.tag_mapping,
                                sample_cutoff = self.sample_cutoff)
        for track in patch.tracks:
            track.samples = self.mock_samples
        patch.mutate_attr("density", limit=0.2)
        for track in patch.tracks:
            self.assertGreaterEqual(track.density, 0.2)
            self.assertLessEqual(track.density, 0.8)

    def test_init_machine(self):
        track = SampleTrack.randomise(track = self.tracks[0],
                                      pool = self.pool,
                                      tags = self.tag_mapping,
                                      sample_cutoff = self.sample_cutoff)
        track.samples = self.mock_samples  # Assign valid samples
        container = Mock()
        machine = track.init_machine(container)
        self.assertEqual(machine.namespace, track.name.capitalize())
        self.assertEqual(machine.samples, self.mock_samples)
            
if __name__ == "__main__":
    unittest.main()
