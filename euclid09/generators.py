def Beat(self, n, rand, pattern, groove, temperature, density, dry_level, **kwargs):
    for i in range(n):
        volume = groove(rand = rand["volume"], i = i)
        if rand["sample"].random() < temperature:
            self.toggle_sample()        
        if (pattern(i) and 
            rand["beat"].random() < density):
            trig_block = self.note(volume = volume,
                                   level = dry_level)
            yield i, trig_block

def GhostEcho(self, n, rand, wet_level,
              sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
              quantise = 4,
              **kwargs):
    for i in range(n):
        if 0 == i % quantise:            
            sh_wet = rand["fx"].choice(sample_hold_levels)
            sh_feedback = rand["fx"].choice(sample_hold_levels)
            trig_block = self.modulation(level = wet_level,
                                         echo_wet = sh_wet,
                                         echo_feedback = sh_feedback)
            yield i, trig_block

if __name__ == "__main__":
    pass
