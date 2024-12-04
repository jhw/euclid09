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

class TrackBase:

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
        return TrackBase(**TrackBase.randomise_params(track, **kwargs))

    @staticmethod
    def from_json(track):
        return TrackBase(**track)

    def __init__(self, name, machine, pattern, groove, seeds, temperature, density):
        self.name = name
        self.machine = machine
        self.pattern = pattern
        self.groove = groove
        self.seeds = seeds
        self.temperature = temperature
        self.density = density

    def clone(self):
        return TrackBase(**self.to_json())

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

"""
Samplers are unique because a sampler's sound isn't generated internally, it has to come from an external source
Each track has a machine bound to it; when a track is rendered, that machine is instantiated
Sampler- based machines require sounds (samples) and also cutoff parameters; you can argue the latter is optional and could be a default arg, but the former is required
Hence any machines which is sampler based needs its own track class, one that contains whatever elements are required for machine initialisation
In the euclid09 implementation, a sampler's sounds come from pool and tags args
Note that a sampler makes use of "sounds" rather than "samples', in an nod towards some kind of machine polymorphism
"""

"""
Detroit unlikely to be the only sampler based class; can imagine one which uses pad/chord/drone samples as a base, and does stuttering
Berlin is different case because the sample there is a "base sample" and not designed to be switched by a client (unless you had a series of base waveforms?)
"""
    
class SamplerTrack(TrackBase):

    @staticmethod
    def randomise_params(track, pool, tags, cutoff,
                         n_sounds = 2, **kwargs):
        # sounds
        base_kwargs = TrackBase.randomise_params(track)
        tag = tags[track["name"]]
        sounds = pool.match(lambda sample: tag in sample.tags)
        random.shuffle(sounds)
        base_kwargs["sounds"] = sounds[:n_sounds]
        base_kwargs["cutoff"] = cutoff
        # seeds
        base_kwargs["seeds"]["sample"] = random_seed()
        return base_kwargs

    @staticmethod
    def randomise(track, **kwargs):
        return SamplerTrack(**SamplerTrack.randomise_params(track = track,
                                                            **kwargs))
    
    @staticmethod
    def from_json(track):
        track["sounds"] = [SVSample(**sample) for sample in track["sounds"]]
        return SamplerTrack(**track)

    def __init__(self, sounds, cutoff, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sounds = sounds
        self.cutoff = cutoff

    def clone(self):
        return SamplerTrack(**self.to_json())

    """
    CLI may have randomised tags, hence pool and tags need to be re- passed to rack on shuffling
    """
    
    def shuffle_sounds(self, pool, tags, **kwargs):
        tag = tags[self.name]
        sounds = pool.match(lambda sample: tag in sample.tags)
        random.shuffle(sounds)
        i = int(random.random() > 0.5)
        self.sounds[i] = sounds[0]

    def init_machine(self, container, colour):
        machine_class = load_class(self.machine)
        return machine_class(container = container,
                             namespace = self.name.capitalize(),
                             colour = colour,
                             sounds = self.sounds,
                             sound_cutoff = self.cutoff) # NB name switch
        
    def to_json(self):
        base_json = super().to_json()
        base_json["sounds"] = copy.deepcopy(self.sounds)
        base_json["cutoff"] = self.cutoff
        return base_json

class Tracks(list):

    @staticmethod
    def randomise(tracks, **kwargs):
        track_instances = []
        for track in tracks:
            track_class = SamplerTrack if does_class_extend(load_class(track["machine"]), sv.machines.SVSamplerMachine) else TrackBase
            track_randomiser = getattr(track_class, "randomise")
            track_instance = track_randomiser(track = track, **kwargs)
            track_instances.append(track_instance)        
        return Tracks(track_instances)

    @staticmethod
    def from_json(tracks):
        return Tracks([SamplerTrack.from_json(track) for track in tracks])

    @staticmethod
    def from_json(tracks):
        track_instances = []
        for track in tracks:
            track_class = SamplerTrack if does_class_extend(load_class(track["machine"]), sv.machines.SVSamplerMachine) else TrackBase
            track_instance = getattr(track_class, "from_json")(track)
            track_instances.append(track_instance)        
        return Tracks(track_instances)
    
    def __init__(self, tracks = None):
        list.__init__(self, tracks if tracks else [])

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
            level = levels[track.name] if track.name in levels else 1
            colour = colours[track.name] if track.name in colours else [127, 127, 127]
            track.render(container = container,
                         generators = generators,
                         dry_level = level,
                         colour = colour)
        
    def to_json(self):
        return [track.to_json()
                for track in self]
        
class Patch:

    @staticmethod
    def randomise(tracks, **kwargs):
        return Patch(tracks = Tracks.randomise(tracks = tracks, **kwargs))

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

    def render(self, container, generators, levels, machine_colours, patch_colour):
        container.spawn_patch(patch_colour)
        self.tracks.render(container = container,
                           generators = generators,
                           levels = levels,
                           colours = machine_colours)
        
    def to_json(self):
        return {"tracks": self.tracks.to_json()}

class Patches(list):

    @staticmethod
    def randomise(tracks, n, **kwargs):
        return Patches([Patch.randomise(tracks = tracks, **kwargs)
                        for i in range(n)])

    @staticmethod
    def from_json(patches):
        return Patches([Patch.from_json(patch) for patch in patches])
    
    def __init__(self, patches = None):
        list.__init__(self, patches if patches else [])

    def clone(self):
        return Patches([patch.clone() for patch in self])
        
    def render(self, container, generators, levels, colours):
        for i, patch in enumerate(self):
            machine_colours = colours["machines"] if "machines" in colours else {}
            patch_colour = colours["patches"][i] if "patches" in colours else [127, 127, 127]
            patch.render(container = container,
                         generators = generators,
                         levels = levels,
                         machine_colours = machine_colours,
                         patch_colour = patch_colour)
    
    def to_json(self):
        return [patch.to_json()
                for patch in self]

class Project:

    @staticmethod
    def randomise(tracks, n, **kwargs):
        return Project(patches = Patches.randomise(tracks = tracks,
                                                   n = n,
                                                   **kwargs))
    @staticmethod
    def from_json(project):
        return Project(patches = Patches.from_json(project["patches"]))
    
    def __init__(self, patches = None):
        self.patches = patches if patches else Patches()

    def render(self, banks, generators, levels,
               colours = {},
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
