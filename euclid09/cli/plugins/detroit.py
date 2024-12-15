from sv.banks import SVBanks
from sv.utils.banks import init_banks

from euclid09.cli.tags import Tags

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

class DetroitSoundPlugin:

    def __init__(self, tracks, terms = Terms):
        self.banks = SVBanks.load_zip(cache_dir="banks")
        self.pool, _ = self.banks.spawn_pool(tag_patterns=terms)
        self.tags = Tags(tracks = tracks,
                         terms = terms).validate().randomise()

    def randomise_tags(self):
        self.tags.randomise()

    def show_tags(self):
        return " ".join([f"{k}={v}" for k, v in self.tags.items()])

    def reset_tags(self):
        self.tags = Tags(tracks=self.tracks,
                         terms=self.tags.terms)

    def filter_sounds(self, tracks):
        sounds = {}
        for track in tracks:
            tag = self.tags[track["name"]]
            track_sounds = self.pool.match(lambda sample: tag in sample.tags)
            sounds[track["name"]] = track_sounds
        return sounds

if __name__ == "___main__":
    pass
