import sv.algos.euclid as euclid
import sv.algos.groove.perkons as perkons

from sv.container import SVContainer
from sv.instruments.nine09.samples import Nine09
from sv.sampler import SVSampleRef as SVSample

from euclid09.generators import *

import copy
import inspect
import random

def random_pattern():
    pattern_kwargs = {k:v for k, v in zip(["pulses", "steps"], random.choice(euclid.TidalPatterns)[:2])}
    return {"mod": "euclid",
            "fn": "bjorklund",
            "args": pattern_kwargs}

def random_groove():
    groove_fns = [name for name, _ in inspect.getmembers(perkons, inspect.isfunction)]    
    return {"mod": "perkons",
            "fn": random.choice(groove_fns)}

def random_seed():
    return int(random.random() * 1e8)

def spawn_function(mod, fn, **kwargs):
    return getattr(eval(mod), fn)

class Track:

    @staticmethod
    def randomise(pool, track, tag_mapping,
                  n_samples = 2,
                  seed_keys = "fx|volume|sample|beat".split("|")):
        tag = tag_mapping[track["name"]]
        samples = pool.match(lambda sample: tag in sample.tags)
        random.shuffle(samples)
        seeds = {key: random_seed()
                 for key in seed_keys}
        return Track(name = track["name"],
                     samples = samples[:n_samples],
                     pattern = random_pattern(),
                     groove = random_groove(),
                     seeds = seeds,
                     temperature = track["temperature"],
                     density = track["density"])

    @staticmethod
    def from_json(track):
        track["samples"] = [SVSample(**sample) for sample in track["samples"]]
        return Track(**track)

    def __init__(self, name, samples, pattern, groove, seeds, temperature, density):
        self.name = name
        self.samples = samples
        self.pattern = pattern
        self.groove = groove
        self.seeds = seeds
        self.temperature = temperature
        self.density = density

    def clone(self):
        return Track(name = self.name,
                     samples = list(self.samples),
                     pattern = copy.deepcopy(self.pattern),
                     groove = copy.deepcopy(self.groove),
                     seeds = dict(self.seeds),
                     temperature = self.temperature,
                     density = self.density)

    def shuffle_samples(self, pool, tag_mapping, **kwargs):
        tag = tag_mapping[self.name]
        samples = pool.match(lambda sample: tag in sample.tags)
        random.shuffle(samples)
        i = int(random.random() > 0.5)
        self.samples[i] = samples[0]

    def shuffle_pattern(self, **kwargs):
        self.pattern = random_pattern()

    def shuffle_groove(self, **kwargs):
        self.groove = random_groove()

    def shuffle_seeds(self, **kwargs):
        key = random.choice(list(self.seeds.keys()))
        self.seeds[key] = random_seed()
    
    def shuffle_temperature(self, limit = 0.25, **kwargs):
        self.temperature = limit + random.random() * (1 - (2 * limit))

    def shuffle_density(self, limit = 0.25, **kwargs):
        self.density = limit + random.random() * (1 - (2 * limit))

    def render(self, container, dry_level, wet_level = 1):
        nine09 = Nine09(container = container,
                        namespace = self.name.capitalize(),
                        samples = self.samples)
        container.add_instrument(nine09)
        pattern = spawn_function(**self.pattern)(**self.pattern["args"])
        groove = spawn_function(**self.groove)
        env = {"dry_level": dry_level,
               "wet_level": wet_level,
               "temperature": self.temperature,
               "density": self.density,
               "pattern": pattern,
               "groove": groove}
        nine09.render(generator = Beat, 
                      seeds = self.seeds,
                      env = env)
        nine09.render(generator = GhostEcho,
                      seeds = self.seeds,
                      env = env)
        
    def to_json(self):
        return {"name": self.name,
                "samples": self.samples,
                "pattern": self.pattern,
                "groove": self.groove,
                "seeds": self.seeds,
                "temperature": self.temperature,
                "density": self.density}

class Tracks(list):

    @staticmethod
    def randomise(pool, tracks, tag_mapping):
        return Tracks([Track.randomise(pool = pool,
                                       track = track,
                                       tag_mapping = tag_mapping)
                       for track in tracks])

    @staticmethod
    def from_json(tracks):
        return Tracks([Track.from_json(track) for track in tracks])
    
    def __init__(self, tracks = []):
        list.__init__(self, tracks)

    def clone(self):
        return Tracks([track.clone() for track in self])

    def randomise_attr(self, attr, **kwargs):
        track = random.choice(self)
        getattr(track, f"shuffle_{attr}")(**kwargs)

    def render(self, container, levels):                
        for track in self:
            track.render(container = container,
                         dry_level = levels[track.name])
        
    def to_json(self):
        return [track.to_json()
                for track in self]
        
class Patch:

    @staticmethod
    def randomise(pool, tracks, tag_mapping):
        return Patch(tracks = Tracks.randomise(pool = pool,
                                               tracks = tracks,
                                               tag_mapping = tag_mapping))

    @staticmethod
    def from_json(patch):
        return Patch(tracks = Tracks.from_json(patch["tracks"]))
    
    def __init__(self, tracks = []):
        self.tracks = tracks

    def clone(self):
        return Patch(tracks = self.tracks.clone())    

    def randomise_attr(self, attr, **kwargs):
        self.tracks.randomise_attr(attr, **kwargs)

    def render(self, container, levels):
        container.spawn_patch()
        self.tracks.render(container = container,
                           levels = levels)
        
    def to_json(self):
        return {"tracks": self.tracks.to_json()}

class Patches(list):

    @staticmethod
    def randomise(pool, tracks, tag_mapping, n):
        return Patches([Patch.randomise(pool = pool,
                                        tracks = tracks,
                                        tag_mapping = tag_mapping)
                        for i in range(n)])

    @staticmethod
    def from_json(patches):
        return Patches([Patch.from_json(patch) for patch in patches])
    
    def __init__(self, patches = []):
        list.__init__(self, patches)

    def clone(self):
        return Patches([patch.clone() for patch in self])
        
    def render(self, banks, levels,
               bpm = 120,
               n_ticks = 16):
        container = SVContainer(banks = banks,
                                bpm = bpm,
                                n_ticks = n_ticks)
        for patch in self:
            patch.render(container,
                         levels = levels)
        return container
    
    def to_json(self):
        return [patch.to_json()
                for patch in self]

if __name__ == "__main__":
    pass
