import random

class Colour(list):

    @staticmethod
    def randomise(offset = 64,
                  contrast = 128,
                  n = 256):
        for i in range(n):
            rgb = [int(offset + random.random() * (255 - offset))
                   for i in range(3)]
            if (max(rgb) - min(rgb)) > contrast:
                return Colour(rgb)
        raise RuntimeError("couldn't find suitable random colour")
        
    def __init__(self, rgb):
        list.__init__(self, rgb)

    def clone(self):
        return Colour(self)

    def mutate(self, range = 32):
        for i, v in enumerate(self):
            q = int(2 * random.random() * range) - range
            self[i] = max(0, min(255, v + q))
        return self
    
class Colours(dict):

    @staticmethod
    def randomise_machines(tracks):
        colours = {}
        for track in tracks:
            colour = Colour.randomise()
            colours[track["name"]] = colour
        return colours

    @staticmethod
    def randomise_patches(patches, quantise = 4):
        colours = []
        for i, patch in enumerate(patches):
            if 0 == i % quantise:                
                colour = Colour.randomise()
            else:
                colour = colours[-1].clone().mutate()
            colours.append(colour)
        return colours
    
    @staticmethod
    def randomise(tracks, patches):
        machine_colours = Colours.randomise_machines(tracks)
        patch_colours = Colours.randomise_patches(patches)
        return Colours(machine_colours = machine_colours,
                       patch_colours = patch_colours)

    def __init__(self, machine_colours, patch_colours):
        dict.__init__(self)
        self["machines"] = machine_colours
        self["patches"] = patch_colours

if __name__ == "__main__":
    pass
