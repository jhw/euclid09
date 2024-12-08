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
        self.cutoff = 0.5                       
        self.mock_sample = {
            "bank_name": "drums",
            "file_path": "kick.wav",
            "note": 36,
            "tags": ["kick"]
        }
        self.mock_sounds = [SVSample(**self.mock_sample) for _ in range(2)]

    def test_shuffle_pattern(self):
        track = SynthTrack.randomise(track=self.tracks[0])
        initial_pattern = track.pattern
        track.shuffle_pattern()
        # self.assertNotEqual(initial_pattern, track.pattern)

    def test_shuffle_groove(self):
        track = SynthTrack.randomise(track=self.tracks[0])
        initial_groove = track.groove
        track.shuffle_groove()
        # self.assertNotEqual(initial_groove, track.groove)

    def test_shuffle_seeds(self):
        track = SynthTrack.randomise(track=self.tracks[0])
        initial_seeds = track.seeds.copy()
        track.shuffle_seeds()
        self.assertNotEqual(initial_seeds, track.seeds)

    def test_shuffle_sounds(self):
        track = SamplerTrack.randomise(track=self.tracks[0],
                                       pool=self.pool,
                                       tags=self.tags,
                                       cutoff=self.cutoff)
        initial_sounds = track.sounds.copy()
        track.shuffle_sounds(pool=self.pool, tags=self.tags)
        # self.assertNotEqual(initial_sounds, track.sounds)

    def test_mutate_attr_with_filter(self):
        tracks = Tracks.randomise(tracks=self.tracks,
                                  pool=self.pool,
                                  tags=self.tags,
                                  cutoff=self.cutoff)
        for track in tracks:
            track.sounds = self.mock_sounds
        filter_fn = lambda t: t.name == "kick"
        tracks.mutate_attr(attr="density", filter_fn=filter_fn)
        for track in tracks:
            if track.name == "kick":
                self.assertGreaterEqual(track.density, 0.0)
                self.assertLessEqual(track.density, 1.0)

    def test_mutate_attr_no_matches(self):
        tracks = Tracks.randomise(tracks=self.tracks,
                                  pool=self.pool,
                                  tags=self.tags,
                                  cutoff=self.cutoff)
        filter_fn = lambda t: t.name == "nonexistent"
        with self.assertRaises(RuntimeError):
            tracks.mutate_attr(attr="density", filter_fn=filter_fn)

    def test_sample_track_creation(self):
        track = SamplerTrack.randomise(track=self.tracks[0],
                                       pool=self.pool,
                                       tags=self.tags,
                                       cutoff=self.cutoff)
        self.assertIsInstance(track, SamplerTrack)
        self.assertEqual(track.name, "kick")
        self.assertEqual(len(track.sounds), 2)
        self.assertIn("mod", track.pattern)
        self.assertIn("fn", track.groove)

    def test_sample_track_clone(self):
        track = SamplerTrack.randomise(track=self.tracks[0],
                                       pool=self.pool,
                                       tags=self.tags,
                                       cutoff=self.cutoff)
        track.sounds = self.mock_sounds
        clone = track.clone()
        self.assertEqual(track.name, clone.name)
        self.assertEqual(track.sounds, clone.sounds)
        self.assertEqual(track.pattern, clone.pattern)
        self.assertEqual(track.groove, clone.groove)

    def test_mutation_tracks(self):
        tracks = Tracks.randomise(tracks=self.tracks,
                                  pool=self.pool,
                                  tags=self.tags,
                                  cutoff=self.cutoff)
        for track in tracks:
            track.sounds = self.mock_sounds
        initial_temperatures = [track.temperature for track in tracks]
        tracks.mutate_attr(attr="temperature", labdlimit=0.1)
        mutated_temperatures = [track.temperature for track in tracks]
        self.assertNotEqual(initial_temperatures, mutated_temperatures)
        for temp in mutated_temperatures:
            self.assertGreaterEqual(temp, 0.0)
            self.assertLessEqual(temp, 1.0)

    def test_mutation_patch(self):
        patch = Patch.randomise(tracks=self.tracks,
                                pool=self.pool,
                                tags=self.tags,
                                cutoff=self.cutoff)
        for track in patch.tracks:
            track.sounds = self.mock_sounds
        initial_densities = [track.density for track in patch.tracks]
        patch.mutate_attr("density", limit=0.2)
        mutated_densities = [track.density for track in patch.tracks]
        self.assertNotEqual(initial_densities, mutated_densities)
        for density in mutated_densities:
            self.assertGreaterEqual(density, 0.0)
            self.assertLessEqual(density, 1.0)

    def test_tracks_randomisation(self):
        tracks = Tracks.randomise(tracks=self.tracks,
                                  pool=self.pool,
                                  tags=self.tags,
                                  cutoff=self.cutoff)
        self.assertIsInstance(tracks, Tracks)
        self.assertEqual(len(tracks), len(self.tracks))
        clone = tracks.clone()
        self.assertEqual(len(clone), len(tracks))
        for t1, t2 in zip(tracks, clone):
            self.assertEqual(t1.name, t2.name)

    def test_tracks_serialization(self):
        tracks = Tracks.randomise(tracks=self.tracks,
                                  pool=self.pool,
                                  tags=self.tags,
                                  cutoff=self.cutoff)
        for track in tracks:
            track.sounds = self.mock_sounds
        serialized = tracks.to_json()
        deserialized = Tracks.from_json(serialized)
        self.assertEqual(len(tracks), len(deserialized))
        for t1, t2 in zip(tracks, deserialized):
            self.assertEqual(t1.name, t2.name)

    def test_patch_creation(self):
        patch = Patch.randomise(tracks=self.tracks,
                                pool=self.pool,
                                tags=self.tags,
                                cutoff=self.cutoff)
        for track in patch.tracks:
            track.sounds = self.mock_sounds
        self.assertIsInstance(patch, Patch)
        clone = patch.clone()
        self.assertEqual(len(clone.tracks), len(patch.tracks))
        serialized = patch.to_json()
        deserialized = Patch.from_json(serialized)
        self.assertEqual(len(deserialized.tracks), len(patch.tracks))

    def test_patches_randomisation(self):
        patches = Patches.randomise(tracks=self.tracks,
                                    pool=self.pool,
                                    tags=self.tags,
                                    cutoff=self.cutoff,
                                    n=3)
        for patch in patches:
            for track in patch.tracks:
                track.sounds = self.mock_sounds
        self.assertIsInstance(patches, Patches)
        self.assertEqual(len(patches), 3)
        clone = patches.clone()
        self.assertEqual(len(clone), len(patches))

    def test_patches_serialization(self):
        patches = Patches.randomise(tracks=self.tracks,
                                    pool=self.pool,
                                    tags=self.tags,
                                    cutoff=self.cutoff,
                                    n=3)
        for patch in patches:
            for track in patch.tracks:
                track.sounds = self.mock_sounds
        serialized = patches.to_json()
        deserialized = Patches.from_json(serialized)
        self.assertEqual(len(deserialized), len(patches))
        for p1, p2 in zip(patches, deserialized):
            self.assertEqual(len(p1.tracks), len(p2.tracks))

    def test_init_machine(self):
        track = SamplerTrack.randomise(track=self.tracks[0],
                                       pool=self.pool,
                                       tags=self.tags,
                                       cutoff=self.cutoff)
        track.sounds = self.mock_sounds
        container = Mock()
        machine = track.init_machine(container, [127, 127, 127])
        self.assertEqual(machine.namespace, track.name.capitalize())
        self.assertEqual(machine.sounds, self.mock_sounds)

    def test_track_polymorphism(self):
        for klass in [SamplerTrack, SynthTrack]:
            track = klass.randomise(track=self.tracks[0],
                                    pool=self.pool,
                                    tags=self.tags,
                                    cutoff=self.cutoff)
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
        container = project.render(banks=banks,
                                   generators=generators)
        self.assertIsNotNone(container)

    def test_patches_freeze(self):
        patches = Patches.randomise(tracks=self.tracks,
                                    pool=self.pool,
                                    tags=self.tags,
                                    cutoff=self.cutoff,
                                    n=5)
        patches.freeze(3)
        for i, patch in enumerate(patches):
            if i < 3:
                self.assertTrue(patch.frozen)
            else:
                self.assertFalse(patch.frozen)

    def test_project_freezing(self):
        project = Project.randomise(tracks=self.tracks,
                                    pool=self.pool,
                                    tags=self.tags,
                                    cutoff=self.cutoff,
                                    n=4)
        project.freeze_patches(2)
        frozen_count = sum(1 for patch in project.patches if patch.frozen)
        self.assertEqual(frozen_count, 2)

    def test_clone_maintains_frozen_state(self):
        patches = Patches.randomise(tracks=self.tracks,
                                    pool=self.pool,
                                    tags=self.tags,
                                    cutoff=self.cutoff,
                                    n=3)
        patches.freeze(2)
        cloned_patches = patches.clone()
        for i, patch in enumerate(cloned_patches):
            self.assertEqual(patch.frozen, i < 2)

if __name__ == "__main__":
    unittest.main()
