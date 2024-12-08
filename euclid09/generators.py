def Beat(self, n, rand, pattern, groove, temperature, density, dry_level, tpb, **kwargs):
    for i in range(n):
        if 0 == i % tpb:
            j = int(i / tpb)
            volume = groove(rand = rand["volume"], i = j)
            if rand["sound"].random() < temperature:
                self.toggle_sound()        
            if (pattern(j) and 
                rand["beat"].random() < density):
                trig_block = self.note(volume = volume,
                                       level = dry_level)
                yield i, trig_block

def GhostEcho(self, n, rand, wet_level, bpm, tpb,
              sample_hold_levels = ["0000", "2000", "4000", "6000", "8000"],
              quantise = 4,
              **kwargs):
    for i in range(n):
        if 0 == i % int(quantise * tpb):
            wet_value = rand["fx"].choice(sample_hold_levels)
            feedback_value = rand["fx"].choice(sample_hold_levels)
            delay_value = hex(int(128 * bpm * tpb * 3 / 10))
            trig_block = self.modulation(level = wet_level,
                                         echo_delay = delay_value,
                                         echo_wet = wet_value,
                                         echo_feedback = feedback_value)
            yield i, trig_block

if __name__ == "__main__":
    pass
