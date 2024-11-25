from sv.banks import SVBanks
from sv.utils.banks import init_banks

from euclid09.base_cli import BaseCLI, load_yaml, assert_head, commit_and_render
from euclid09.generators import Beat, GhostEcho
from euclid09.model import Patches
from euclid09.parse import parse_line

import boto3
import os
import random
import sys

class ArrangerCLI(BaseCLI):

    prompt = ">>> "
    intro = "Welcome to the euclid09 arranger CLI ;)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @assert_head
    @parse_line([{"name": "indexing", "type": "hexstr"}])
    @commit_and_render
    def do_randomise(self, indexing,
                      phrase_size = 4,
                      patterns = [[0, 1, 0, 0],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1],
                                  [0, 0, 0, 1],
                                  [0, 0, 0, 1],
                                  [0, 1, 0, 2]]):
        patches = self.git.head.content
        roots = [patches[i % len(patches)] for i in indexing]
        n_phrases = int(self.n_patches / phrase_size)
        arrangement = Patches()
        for i in range(n_phrases):
            pattern = random.choice(patterns)
            random.shuffle(roots)
            for j in pattern:
                patch = roots[j].clone()
                arrangement.append(patch)
        return arrangement
           
def env_value(key):
    if key not in os.environ or os.environ[key] in ["", None]:
        raise RuntimeError(f"{key} not defined")
    return os.environ[key]

if __name__ == "__main__":
    try:
        s3 = boto3.client("s3")
        bucket_name = env_value("SV_BANKS_HOME")
        init_banks(s3=s3, bucket_name=bucket_name)
        banks = SVBanks.load_zip()
        terms = load_yaml("terms.yaml")
        pool, _ = banks.spawn_pool(tag_patterns = terms)
        tracks = load_yaml("tracks.yaml")
        tags = {track["name"]: track["name"] for track in tracks}
        ArrangerCLI(banks = banks,
                    pool = pool,
                    generators = [Beat, GhostEcho],
                    tracks = tracks,
                    tags = tags,
                    terms = terms).cmdloop()
    except RuntimeError as error:
        logging.error(str(error))
