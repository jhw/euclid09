import random

class Tags(dict):

    def __init__(self, tracks, terms):
        dict.__init__(self, {track["name"]:track["name"] for track in tracks})
        self.terms = terms

    def validate(self):
        for key in self:
            if key not in self:
                raise RuntimeError(f"track '{key}' not present in terms")
        return self

    def randomise(self):
        options = list(self.terms.keys())
        for key in self:
            self[key] = random.choice(options)
        return self
                
if __name__ == "__main__":
    pass
