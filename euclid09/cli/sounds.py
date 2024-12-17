from sv.banks import SVBanks
from sv.project import load_class
        
class Sounds:

    def __init__(self, tracks, **kwargs):
        self.tracks = tracks
        for track in tracks:
            tokens = track["machine"].split(".")
            mod_name, class_name = tokens[-2], tokens[-1].replace("Machine", "SoundFactory")            
            factory_class = load_class(f"euclid09.cli.factories.{mod_name}.{class_name}")
            track["sound"] = factory_class(track = track, **kwargs)

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
