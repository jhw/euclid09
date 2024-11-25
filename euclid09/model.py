import sv.algos.euclid as euclid
import sv.algos.groove.perkons as perkons

from sv.container import SVContainer
from sv.sampler import SVSampleRef as SVSample
from sv.project import load_class

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

class SynthTrack:

    @staticmethod
    def randomise_params(track, seed_keys = "fx|volume|beat".split("|"), **kwargs):
        seeds = {key: random_seed()
                 for key in seed_keys}
        return {"name": track["name"],
                "machine": track["machine"],
                "type": track["type"],
                "pattern": random_pattern(),
                "groove": random_groove(),
                "seeds": seeds,
                "temperature": track["temperature"],
                "density": track["density"]}

    @staticmethod
    def randomise(track, **kwargs):
        return SynthTrack(**SynthTrack.randomise_params(track, **kwargs))

    @staticmethod
    def from_json(track):
        return SynthTrack(**track)

    def __init__(self, name, machine, type, pattern, groove, seeds, temperature, density):
        self.name = name
        self.machine = machine
        self.type = type
        self.pattern = pattern
        self.groove = groove
        self.seeds = seeds
        self.temperature = temperature
        self.density = density

    def clone(self):
        return SynthTrack(**self.to_json())

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

    def init_machine(self, container):
        machine_class = load_class(self.machine)
        return machine_class(container = container,
                             namespace = self.name.capitalize())
        
    def render(self, container, generators, dry_level, wet_level = 1):
        machine = self.init_machine(container)
        container.add_machine(machine)
        pattern = spawn_function(**self.pattern)(**self.pattern["args"])
        groove = spawn_function(**self.groove)
        env = {"dry_level": dry_level,
               "wet_level": wet_level,
               "temperature": self.temperature,
               "density": self.density,
               "pattern": pattern,
               "groove": groove}
        for generator in generators:
            machine.render(generator = generator,
                           seeds = self.seeds,
                           env = env)
        
    def to_json(self):
        return {"name": self.name,
                "machine": self.machine,
                "type": self.type,
                "pattern": copy.deepcopy(self.pattern),
                "groove": copy.deepcopy(self.groove),
                "seeds": copy.deepcopy(self.seeds),
                "temperature": self.temperature,
                "density": self.density}

class SampleTrack(SynthTrack):

    @staticmethod
    def randomise_params(pool, track, tags,
                         n_samples = 2, **kwargs):
        # samples
        base_kwargs = SynthTrack.randomise_params(track)
        tag = tags[track["name"]]
        samples = pool.match(lambda sample: tag in sample.tags)
        random.shuffle(samples)
        base_kwargs["samples"] = samples[:n_samples]
        # seeds
        base_kwargs["seeds"]["sample"] = random_seed()
        return base_kwargs

    @staticmethod
    def randomise(pool, track, tags, **kwargs):
        return SampleTrack(**SampleTrack.randomise_params(pool, track, tags, **kwargs))
    
    @staticmethod
    def from_json(track):
        track["samples"] = [SVSample(**sample) for sample in track["samples"]]
        return SampleTrack(**track)

    def __init__(self, samples, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.samples = samples

    def clone(self):
        return SampleTrack(**self.to_json())

    def shuffle_samples(self, pool, tags, **kwargs):
        tag = tags[self.name]
        samples = pool.match(lambda sample: tag in sample.tags)
        random.shuffle(samples)
        i = int(random.random() > 0.5)
        self.samples[i] = samples[0]

    def init_machine(self, container):
        machine_class = load_class(self.machine)
        return machine_class(container = container,
                             namespace = self.name.capitalize(),
                             samples = self.samples)
        
    def to_json(self):
        base_json = super().to_json()
        base_json["samples"] = copy.deepcopy(self.samples)
        return base_json

class Tracks(list):

    @staticmethod
    def randomise(pool, tracks, tags):
        track_instances = []
        for track in tracks:
            track_class = SampleTrack if track["type"] == "sample" else SynthTrack
            params_randomiser = getattr(track_class, "randomise_params")
            track_params = params_randomiser(**{"pool": pool,
                                                "track": track,
                                                "tags": tags})
            track_instance = track_class(**track_params)
            track_instances.append(track_instance)        
        return Tracks(track_instances)

    @staticmethod
    def from_json(tracks):
        return Tracks([SampleTrack.from_json(track) for track in tracks])

    @staticmethod
    def from_json(tracks):
        track_instances = []
        for track in tracks:
            track_class = SampleTrack if track["type"] == "sample" else SynthTrack
            track_instance = getattr(track_class, "from_json")(track)
            track_instances.append(track_instance)        
        return Tracks(track_instances)
    
    def __init__(self, tracks = []):
        list.__init__(self, tracks)

    def clone(self):
        return Tracks([track.clone() for track in self])

    def mutate_attr(self, attr, **kwargs):
        track = random.choice(self)
        getattr(track, f"shuffle_{attr}")(**kwargs)

    def render(self, container, generators, levels):                
        for track in self:
            track.render(container = container,
                         generators = generators,
                         dry_level = levels[track.name])
        
    def to_json(self):
        return [track.to_json()
                for track in self]
        
class Patch:

    @staticmethod
    def randomise(pool, tracks, tags):
        return Patch(tracks = Tracks.randomise(pool = pool,
                                               tracks = tracks,
                                               tags = tags))

    @staticmethod
    def from_json(patch):
        return Patch(tracks = Tracks.from_json(patch["tracks"]))
    
    def __init__(self, tracks = []):
        self.tracks = tracks

    def clone(self):
        return Patch(tracks = self.tracks.clone())    

    def mutate_attr(self, attr, **kwargs):
        self.tracks.mutate_attr(attr, **kwargs)

    def render(self, container, generators, levels):
        container.spawn_patch()
        self.tracks.render(container = container,
                           generators = generators,
                           levels = levels)
        
    def to_json(self):
        return {"tracks": self.tracks.to_json()}

class Patches(list):

    @staticmethod
    def randomise(pool, tracks, tags, n):
        return Patches([Patch.randomise(pool = pool,
                                        tracks = tracks,
                                        tags = tags)
                        for i in range(n)])

    @staticmethod
    def from_json(patches):
        return Patches([Patch.from_json(patch) for patch in patches])
    
    def __init__(self, patches = []):
        list.__init__(self, patches)

    def clone(self):
        return Patches([patch.clone() for patch in self])
        
    def render(self, banks, generators, levels,
               bpm = 120,
               n_ticks = 16):
        container = SVContainer(banks = banks,
                                bpm = bpm,
                                n_ticks = n_ticks)
        for patch in self:
            patch.render(container = container,
                         generators = generators,
                         levels = levels)
        return container
    
    def to_json(self):
        return [patch.to_json()
                for patch in self]

if __name__ == "__main__":
    pass
