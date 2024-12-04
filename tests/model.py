from sv.machines import SVMachineTrigs
from euclid09.model import *

from unittest.mock import Mock, patch

import unittest

class ModelTest(unittest.TestCase):

    def setUp(self):
        self.pool = Mock()
        self.pool.match = Mock(return_value=[Mock(tag='sample') for _ in range(5)])
        self.tracks = [
            {"name": "kick",
             "machine": "sv.machines.detroit.Detroit",
             "temperature": 0.5,
             "density": 0.5},
            {"name": "clap",
             "machine": "sv.machines.detroit.Detroit",
             "temperature": 0.25,
             "density": 0.25}
        ]
        self.tags = {"kick": "sample", "clap": "sample"}
        self.cutoff  = 0.5                       
        self.mock_sample = {
            "bank_name": "drums",
            "file_path": "kick.wav",
            "note": 36,
            "tags": ["kick"]
        }
        self.mock_sounds = [SVSample(**self.mock_sample) for _ in range(2)]

    def test_sample_track_creation(self):
        track = SamplerTrack.randomise(track = self.tracks[0],
                                      pool = self.pool,
                                      tags = self.tags,
                                      cutoff = self.cutoff)
        self.assertIsInstance(track, SamplerTrack)
        self.assertEqual(track.name, "kick")
        self.assertEqual(len(track.sounds), 2)
        self.assertIn("mod", track.pattern)
        self.assertIn("fn", track.groove)

    def test_sample_track_clone(self):
        track = SamplerTrack.randomise(track = self.tracks[0],
                                      pool = self.pool,
                                      tags = self.tags,
                                      cutoff = self.cutoff)
        track.sounds = self.mock_sounds
        clone = track.clone()
        self.assertEqual(track.name, clone.name)
        self.assertEqual(track.sounds, clone.sounds)
        self.assertEqual(track.pattern, clone.pattern)
        self.assertEqual(track.groove, clone.groove)

    def test_sample_track_serialization(self):
        track = SamplerTrack.randomise(track = self.tracks[0],
                                      pool = self.pool,
                                      tags = self.tags,
                                      cutoff = self.cutoff)
        track.sounds = self.mock_sounds
        serialized = track.to_json()
        deserialized = SamplerTrack.from_json(serialized)
        self.assertEqual(track.name, deserialized.name)
        self.assertEqual(track.pattern, deserialized.pattern)
        self.assertEqual(track.groove, deserialized.groove)

    def test_tracks_randomisation(self):
        tracks = Tracks.randomise(tracks = self.tracks,
                                  pool = self.pool,
                                  tags = self.tags,
                                  cutoff = self.cutoff)
        self.assertIsInstance(tracks, Tracks)
        self.assertEqual(len(tracks), len(self.tracks))
        clone = tracks.clone()
        self.assertEqual(len(clone), len(tracks))
        for t1, t2 in zip(tracks, clone):
            self.assertEqual(t1.name, t2.name)

    def test_tracks_serialization(self):
        tracks = Tracks.randomise(tracks = self.tracks,
                                  pool = self.pool,
                                  tags = self.tags,
                                  cutoff = self.cutoff)
        for track in tracks:
            track.sounds = self.mock_sounds
        serialized = tracks.to_json()
        deserialized = Tracks.from_json(serialized)
        self.assertEqual(len(tracks), len(deserialized))
        for t1, t2 in zip(tracks, deserialized):
            self.assertEqual(t1.name, t2.name)

    def test_patch_creation(self):
        patch = Patch.randomise(tracks = self.tracks,
                                pool = self.pool,
                                tags = self.tags,
                                cutoff = self.cutoff)
        for track in patch.tracks:
            track.sounds = self.mock_sounds
        self.assertIsInstance(patch, Patch)
        clone = patch.clone()
        self.assertEqual(len(clone.tracks), len(patch.tracks))
        serialized = patch.to_json()
        deserialized = Patch.from_json(serialized)
        self.assertEqual(len(deserialized.tracks), len(patch.tracks))

    def test_patches_randomisation(self):
        patches = Patches.randomise(tracks = self.tracks,
                                    pool = self.pool,
                                    tags = self.tags,
                                    cutoff = self.cutoff,
                                    n = 3)
        for patch in patches:
            for track in patch.tracks:
                track.sounds = self.mock_sounds
        self.assertIsInstance(patches, Patches)
        self.assertEqual(len(patches), 3)
        clone = patches.clone()
        self.assertEqual(len(clone), len(patches))

    def test_patches_serialization(self):
        patches = Patches.randomise(tracks = self.tracks,
                                    pool = self.pool,
                                    tags = self.tags,
                                    cutoff = self.cutoff,
                                    n = 3)
        for patch in patches:
            for track in patch.tracks:
                track.sounds = self.mock_sounds
        serialized = patches.to_json()
        deserialized = Patches.from_json(serialized)
        self.assertEqual(len(deserialized), len(patches))
        for p1, p2 in zip(patches, deserialized):
            self.assertEqual(len(p1.tracks), len(p2.tracks))

    def test_mutation_tracks(self):
        tracks = Tracks.randomise(tracks = self.tracks,
                                  pool = self.pool,
                                  tags = self.tags,
                                  cutoff = self.cutoff)
        for track in tracks:
            track.sounds = self.mock_sounds
        tracks.randomise_attr(attr = "temperature", labdlimit=0.1)
        for track in tracks:
            self.assertGreaterEqual(track.temperature, 0.1)
            self.assertLessEqual(track.temperature, 0.9)

    def test_mutation_patch(self):
        patch = Patch.randomise(tracks = self.tracks,
                                pool = self.pool,
                                tags = self.tags,
                                cutoff = self.cutoff)
        for track in patch.tracks:
            track.sounds = self.mock_sounds
        patch.randomise_attr("density", limit=0.2)
        for track in patch.tracks:
            self.assertGreaterEqual(track.density, 0.2)
            self.assertLessEqual(track.density, 0.8)

    def test_init_machine(self):
        track = SamplerTrack.randomise(track = self.tracks[0],
                                      pool = self.pool,
                                      tags = self.tags,
                                      cutoff = self.cutoff)
        track.sounds = self.mock_sounds  # Assign valid sounds
        container = Mock()
        machine = track.init_machine(container, [127, 127, 127])
        self.assertEqual(machine.namespace, track.name.capitalize())
        self.assertEqual(machine.sounds, self.mock_sounds)

    def test_track_polymorphism(self):
        for klass in [SamplerTrack,
                      SynthTrack]:
            track = klass.randomise(track = self.tracks[0],
                                    pool = self.pool,
                                    tags = self.tags,
                                    cutoff = self.cutoff)
            self.assertEqual(track.name, "kick")

    def test_project_creation(self):
        project = Project.randomise(tracks=self.tracks,
                                    pool=self.pool,
                                    tags=self.tags,
                                    cutoff=self.cutoff,
                                    n=3)
        for patch in project.patches:
            for track in patch.tracks:
                track.sounds = self.mock_sounds
        self.assertIsInstance(project, Project)
        self.assertEqual(len(project.patches), 3)
        clone = project.clone()
        self.assertEqual(len(clone.patches), len(project.patches))

    def test_project_serialization(self):
        project = Project.randomise(tracks=self.tracks,
                                    pool=self.pool,
                                    tags=self.tags,
                                    cutoff=self.cutoff,
                                    n=3)
        for patch in project.patches:
            for track in patch.tracks:
                track.sounds = self.mock_sounds
        serialized = project.to_json()
        deserialized = Project.from_json(serialized)
        self.assertEqual(len(deserialized.patches), len(project.patches))
        for p1, p2 in zip(project.patches, deserialized.patches):
            self.assertEqual(len(p1.tracks), len(p2.tracks))

    def test_project_render(self):
        project = Project.randomise(tracks=self.tracks,
                                    pool=self.pool,
                                    tags=self.tags,
                                    cutoff=self.cutoff,
                                    n=2)
        for patch in project.patches:
            for track in patch.tracks:
                track.sounds = self.mock_sounds
        banks = Mock()
        def mock_generator(machine, *args, **kwargs):
            yield 0, SVMachineTrigs([])
        generators = [mock_generator]
        container = project.render(banks = banks,
                                   generators = generators)
        self.assertIsNotNone(container)        
            
if __name__ == "__main__":
    unittest.main()
