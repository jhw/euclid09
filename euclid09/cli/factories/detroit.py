from sv.banks import SVBanks

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
        
if __name__ == "___main__":
    pass
