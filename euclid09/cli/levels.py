from collections import OrderedDict

class Levels(OrderedDict):

    def __init__(self, tracks):
        OrderedDict.__init__(self, {track["name"]: 1 for track in tracks})

    def mute(self, key):
        for track_name in self:
            self[track_name] = 0 if track_name == key else 1
        return self

        
    def solo(self, key):
        for track_name in self:
            self[track_name] = 1 if track_name == key else 0
        return self

    @property
    def solo_key(self):
        if self.is_solo:
            for k, v in self.items():
                if v == 1:
                    return k[:3]
        return None

    @property
    def short_code(self):
        return "".join([k[0] if self[k] == 1 else "x" for k in sorted(list(self.keys()))])

if __name__ == "__main__":
    pass
