from sv.banks import SVBanks
from sv.project import load_class

import random
import yaml

Terms = yaml.safe_load("""
kick: (kick)|(kik)|(kk)|(bd)
bass: (bass)
kick-bass: (kick)|(kik)|(kk)|(bd)|(bass)
snare: (snare)|(sn)|(sd)
clap: (clap)|(clp)|(cp)|(hc)
snare-clap: (snare)|(sn)|(sd)|(clap)|(clp)|(cp)|(hc)
hat: (oh)|( ch)|(open)|(closed)|(hh)|(hat)
perc: (perc)|(prc)|(rim)|(tom)|(cow)|(rs)
sync: (syn)|(blip)
all-perc: (oh)|( ch)|(open)|(closed)|(hh)|(hat)|(perc)|(prc)|(rim)|(tom)|(cow)|(rs)|(syn)|(blip)
arcade: (arc)
fx: (fx)
glitch: (devine)|(glitch)|(gltch)
noise: (nois)
fm: (fm)
stab: (chord)|(stab)|(piano)
break: (break)|(brk)|(cut)
chord: (chord)
drone: (dron)
pad: (pad)
sweep: (swp)|(sweep)
""")

Banks = SVBanks.load_zip(cache_dir="banks")          

class DetroitSoundFactory:

    def __init__(self, track, cutoff, banks = Banks, terms = Terms, **kwargs):
        self.banks = banks
        self.pool, _ = self.banks.spawn_pool(tag_patterns = terms)
        self.value = self.default_value = track["tag"]
        self.options = list(terms.keys())
        self.cutoff = cutoff

    def randomise(self):
        self.value = random.choice(self.options)        

    def reset(self):
        self.value = self.default_value
        
    def render(self):
        sounds = self.pool.match(lambda sample: self.value in sample.tags)
        for sound in sounds:
            sound.cutoff = self.cutoff
        return sounds
        
class Sounds:

    def __init__(self, tracks, **kwargs):
        self.tracks = tracks
        for track in tracks:
            factory_class = load_class("euclid09.cli.sounds.%s" % track["machine"].split(".")[-1].replace("Machine", "SoundFactory"))
            track["sound"] = factory_class(track = track,
                                           **kwargs)

    def show_mapping(self):
        return ", ".join([f"{track['name']}={track['sound'].value}" for track in self.tracks])

    def randomise_mapping(self):
        for track in self.tracks:
            track["sound"].randomise()

    def reset_mapping(self, tracks):
        for track in self.tracks:
            track["sound"].reset()

    @property
    def banks(self):
        banks = SVBanks()
        for track in self.tracks:
            sound = track["sound"]
            if hasattr(sound, "banks"):
                banks += sound.banks
        return banks        
            
    def render(self):
        return {track["name"]: track["sound"].render()
                for track in self.tracks}

if __name__ == "___main__":
    pass
