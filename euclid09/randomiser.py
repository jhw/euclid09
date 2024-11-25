from sv.banks import SVBanks
from sv.utils.banks import init_banks

from euclid09.base_cli import BaseCLI, load_yaml, assert_head, commit_and_render
from euclid09.generators import Beat, GhostEcho
from euclid09.model import Patches
from euclid09.parse import parse_line

import boto3
import os
import sys

class RandomiserCLI(BaseCLI):

    prompt = ">>> "
    intro = "Welcome to the euclid09 randomiser CLI ;)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @commit_and_render
    def do_randomise_patches(self, _):
        return Patches.randomise(pool=self.pool,
                                 tracks=self.tracks,
                                 tags=self.tags,
                                 n=self.n_patches)

    @assert_head
    @parse_line([{"name": "i", "type": "int"}])
    @commit_and_render
    def do_clone_patch(self, i):
        patches = self.git.head.content
        root = patches[i % len(patches)]
        return Patches([root.clone() for i in range(self.n_patches)])
        
    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_mutate_samples(self, n):
        patches = self.git.head.content.clone()
        for patch in patches[1:]:
            for _ in range(n):
                patch.mutate_attr(attr="samples", pool=self.pool, tags=self.tags)
        return patches

    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_mutate_pattern(self, n):
        patches = self.git.head.content.clone()
        for patch in patches[1:]:
            for _ in range(n):
                patch.mutate_attr(attr="pattern")
        return patches

    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_mutate_seeds(self, n):
        patches = self.git.head.content.clone()
        for patch in patches[1:]:
            for _ in range(n):
                patch.mutate_attr(attr="seeds")
        return patches
           
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
        RandomiserCLI(banks = banks,
                      pool = pool,
                      generators = [Beat, GhostEcho],
                      tracks = tracks,
                      tags = tags,
                      terms = terms).cmdloop()
    except RuntimeError as error:
        logging.error(str(error))
