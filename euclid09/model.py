import sv.algos.euclid as euclid
import sv.algos.groove.perkons as perkons

from sv.container import SVContainer
from sv.sampler import SVSample
from sv.project import load_class, does_class_extend

import copy
import inspect
import random
import sv # so machine classes can be dynamically accessed

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

    def __init__(self, name, machine, pattern, groove, seeds, temperature, density):
        self.name = name
        self.machine = machine
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

    def init_machine(self, container, colour):
        machine_class = load_class(self.machine)
        return machine_class(container = container,
                             namespace = self.name.capitalize(),
                             colour = colour)
        
    def render(self, container, generators, dry_level, colour, wet_level = 1):
        machine = self.init_machine(container, colour)
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
                "pattern": copy.deepcopy(self.pattern),
                "groove": copy.deepcopy(self.groove),
                "seeds": copy.deepcopy(self.seeds),
                "temperature": self.temperature,
                "density": self.density}

class SampleTrack(SynthTrack):

    @staticmethod
    def randomise_params(track, pool, tags, cutoff,
                         n_samples = 2, **kwargs):
        # samples
        base_kwargs = SynthTrack.randomise_params(track)
        tag = tags[track["name"]]
        samples = pool.match(lambda sample: tag in sample.tags)
        random.shuffle(samples)
        base_kwargs["samples"] = samples[:n_samples]
        base_kwargs["cutoff"] = cutoff
        # seeds
        base_kwargs["seeds"]["sample"] = random_seed()
        return base_kwargs

    @staticmethod
    def randomise(track, pool, tags, cutoff, **kwargs):
        return SampleTrack(**SampleTrack.randomise_params(track = track,
                                                          pool = pool,
                                                          tags = tags,
                                                          cutoff = cutoff,
                                                          **kwargs))
    
    @staticmethod
    def from_json(track):
        track["samples"] = [SVSample(**sample) for sample in track["samples"]]
        return SampleTrack(**track)

    def __init__(self, samples, cutoff, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.samples = samples
        self.cutoff = cutoff

    def clone(self):
        return SampleTrack(**self.to_json())

    def shuffle_samples(self, pool, tags, **kwargs):
        tag = tags[self.name]
        samples = pool.match(lambda sample: tag in sample.tags)
        random.shuffle(samples)
        i = int(random.random() > 0.5)
        self.samples[i] = samples[0]

    def init_machine(self, container, colour):
        machine_class = load_class(self.machine)
        return machine_class(container = container,
                             namespace = self.name.capitalize(),
                             colour = colour,
                             samples = self.samples,
                             sample_cutoff = self.cutoff) # NB name switch
        
    def to_json(self):
        base_json = super().to_json()
        base_json["samples"] = copy.deepcopy(self.samples)
        base_json["cutoff"] = self.cutoff
        return base_json

class Tracks(list):

    @staticmethod
    def randomise(tracks, pool, tags, cutoff):
        track_instances = []
        for track in tracks:
            track_class = SampleTrack if does_class_extend(load_class(track["machine"]), sv.machines.SVSamplerMachine) else SynthTrack
            track_randomiser = getattr(track_class, "randomise")
            track_instance = track_randomiser(**{"track": track,
                                                 "pool": pool,
                                                 "tags": tags,
                                                 "cutoff": cutoff})
            track_instances.append(track_instance)        
        return Tracks(track_instances)

    @staticmethod
    def from_json(tracks):
        return Tracks([SampleTrack.from_json(track) for track in tracks])

    @staticmethod
    def from_json(tracks):
        track_instances = []
        for track in tracks:
            track_class = SampleTrack if does_class_extend(load_class(track["machine"]), sv.machines.SVSamplerMachine) else SynthTrack
            track_instance = getattr(track_class, "from_json")(track)
            track_instances.append(track_instance)        
        return Tracks(track_instances)
    
    def __init__(self, tracks = []):
        list.__init__(self, tracks)

    def clone(self):
        return Tracks([track.clone() for track in self])

    def randomise_attr(self, attr, filter_fn = lambda x: True, **kwargs):
        tracks = [track for track in self
                  if filter_fn(track)]
        if tracks == []:
            raise RuntimeError("no tracks found to mutate")
        track = random.choice(tracks)
        getattr(track, f"shuffle_{attr}")(**kwargs)

    def render(self, container, generators, levels, colours):                
        for track in self:
            track.render(container = container,
                         generators = generators,
                         dry_level = levels[track.name],
                         colour = colours[track.name])
        
    def to_json(self):
        return [track.to_json()
                for track in self]
        
class Patch:

    @staticmethod
    def randomise(tracks, pool, tags, cutoff):
        return Patch(tracks = Tracks.randomise(tracks = tracks,
                                               pool = pool,
                                               tags = tags,
                                               cutoff = cutoff))

    @staticmethod
    def from_json(patch):
        return Patch(tracks = Tracks.from_json(patch["tracks"]))
    
    def __init__(self, tracks = Tracks()):
        self.tracks = tracks

    def clone(self):
        return Patch(tracks = self.tracks.clone())    

    def randomise_attr(self, attr, filter_fn = lambda x: True, **kwargs):
        self.tracks.randomise_attr(attr = attr,
                                filter_fn = filter_fn,
                                **kwargs)

    def render(self, container, generators, levels, mod_colours, pat_colour):
        container.spawn_patch(pat_colour)
        self.tracks.render(container = container,
                           generators = generators,
                           levels = levels,
                           colours = mod_colours)
        
    def to_json(self):
        return {"tracks": self.tracks.to_json()}

class Patches(list):

    @staticmethod
    def randomise(tracks, pool, tags, cutoff, n):
        return Patches([Patch.randomise(tracks = tracks,
                                        pool = pool,
                                        tags = tags,
                                        cutoff = cutoff)
                        for i in range(n)])

    @staticmethod
    def from_json(patches):
        return Patches([Patch.from_json(patch) for patch in patches])
    
    def __init__(self, patches = []):
        list.__init__(self, patches)

    def clone(self):
        return Patches([patch.clone() for patch in self])
        
    def render(self, container, generators, levels, colours):
        for i, patch in enumerate(self):
            patch.render(container = container,
                         generators = generators,
                         levels = levels,
                         mod_colours = colours["modules"],
                         pat_colour = colours["patches"][i])
    
    def to_json(self):
        return [patch.to_json()
                for patch in self]

class Project:

    @staticmethod
    def randomise(tracks, pool, cutoff, tags, n):
        return Project(patches = Patches.randomise(tracks = tracks,
                                                   pool = pool,
                                                   cutoff = cutoff,
                                                   tags = tags,
                                                   n = n))               
    @staticmethod
    def from_json(project):
        return Project(patches = Patches.from_json(project["patches"]))
    
    def __init__(self, patches = Patches()):
        self.patches = patches

    def render(self, banks, generators, levels, colours,
               bpm = 120,
               n_ticks = 16):
        container = SVContainer(banks = banks,
                                bpm = bpm,
                                n_ticks = n_ticks)
        self.patches.render(container = container,
                            generators = generators,
                            levels = levels,
                            colours = colours)
        return container
        
    def clone(self):
        return Project(patches = self.patches.clone())

    def to_json(self):
        return {"patches": self.patches.to_json()}
            
if __name__ == "__main__":
    pass
