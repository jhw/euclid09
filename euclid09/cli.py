from sv.banks import SVBanks
from sv.utils.banks import init_banks
from sv.utils.export import export_wav
from sv.utils.naming import random_name

from euclid09.generators import Beat, GhostEcho
from euclid09.git import Git
from euclid09.model import Patches, SampleTrack
from euclid09.parse import parse_line

from collections import OrderedDict

import boto3
import cmd
import logging
import os
import random
import sys
import yaml
import zipfile

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(levelname)s: %(message)s")

def load_yaml(file_name):
    return yaml.safe_load(open("/".join(__file__.split("/")[:-1] + [file_name])).read())

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
    def short_code(self):
        return "".join([k[0] if v == 1 else "x" for k, v in self.items()])

def assert_head(fn):
    def wrapped(self, *args, **kwargs):
        try:
            if self.git.is_empty():
                raise RuntimeError("Please create a commit first")
            return fn(self, *args, **kwargs)
        except RuntimeError as error:            
            logging.warning(str(error))
    return wrapped
    
def commit_and_render(fn):
    def wrapped(self, *args, **kwargs):
        patches = fn(self, *args, **kwargs)
        levels = Levels(self.tracks)
        container = patches.render(banks=self.banks,
                                   generators = self.generators,
                                   levels=levels)
        commit_id = self.git.commit(patches)
        if not os.path.exists("tmp/sunvox"):
            os.makedirs("tmp/sunvox")
        container.write_project(f"tmp/sunvox/{commit_id}.sunvox")
    return wrapped

class Euclid09CLI(cmd.Cmd):

    prompt = ">>> "
    intro = "Welcome to the Euclid09 CLI ;)"

    def __init__(self, banks, pool, tracks, generators, tags, terms, n_patches = 16):
        super().__init__()
        self.banks = banks
        self.pool = pool
        self.tracks = tracks
        self.generators = generators                
        self.tags = dict(tags)
        self.terms = terms
        self.n_patches = n_patches
        self.git = Git("tmp/git")

    def preloop(self):
        logging.info("Fetching commits ...")
        self.git.fetch()

    def postloop(self):
        logging.info("Pushing commits ...")
        self.git.push()
    
    ### tags

    def do_show_tags(self, _):
        logging.info(yaml.safe_dump(self.tags, default_flow_style=False))
    
    def do_randomise_tags(self, _):
        term_keys = list(self.terms.keys())
        tags = {}
        for key in self.tags:
            tag = random.choice(term_keys)
            tags[key] = tag
            term_keys.remove(tag)
        self.tags = tags
        self.do_show_tags(None)

    def do_reset_tags(self, _):
        tags={track["name"]: track["name"] for track in self.tracks}
        self.tags = tags
        self.do_show_tags(None)

    ### patches

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
                patch.randomise_attr(attr="samples", pool=self.pool, tags=self.tags)
        return patches

    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_mutate_pattern(self, n):
        patches = self.git.head.content.clone()
        for patch in patches[1:]:
            for _ in range(n):
                patch.randomise_attr(attr="pattern")
        return patches

    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_mutate_seeds(self, n):
        patches = self.git.head.content.clone()
        for patch in patches[1:]:
            for _ in range(n):
                patch.randomise_attr(attr="seeds")
        return patches
           
    ### export
    
    @assert_head
    def do_export(self, _):
        if not os.path.exists("tmp/wav"):
            os.makedirs("tmp/wav")
        commit_id = self.git.head.commit_id
        zip_name = f"tmp/wav/{commit_id.slug}.zip"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            levels = [Levels(self.tracks)]
            for track in self.tracks:
                levels.append(Levels(self.tracks).solo(track["name"]))
                levels.append(Levels(self.tracks).mute(track["name"]))
            patches = self.git.head.content
            for levels_ in levels:
                container = patches.render(banks = self.banks,
                                           generators = self.generators,
                                           levels = levels_)
                project = container.render_project()
                wav_io = export_wav(project=project)
                wav_name = f"{commit_id.short_name}-{levels_.short_code}.wav"
                logging.info(wav_name)
                zip_file.writestr(wav_name, wav_io.getvalue())

    ### git

    def do_git_head(self, _):
        if self.git.is_empty():
            logging.warning("Git has no commits")
        else:
            logging.info(f"HEAD is {self.git.head.commit_id}")

    def do_git_log(self, _):
        for commit in self.git.commits:
            logging.info(commit.commit_id)

    def do_git_undo(self, _):
        self.git.undo()

    def do_git_redo(self, _):
        self.git.redo()

    ### project management

    def do_clean_projects(self, _):
        while True:
            answer = input(f"Are you sure ?: ")
            if answer == "y":
                for dir_name in ["tmp/git", "tmp/sunvox", "tmp/wav"]:
                    if os.path.exists(dir_name):
                        for filename in os.listdir(dir_name):
                            file_path = os.path.join(dir_name, filename)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                self.git = Git("tmp/git")
                break
            elif answer == "n":
                break
            elif answer == "q":
                return 

    ### exit
        
    def do_exit(self, _):
        return self.do_quit(None)

    def do_quit(self, _):
        logging.info("Exiting ..")
        return True

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
        Euclid09CLI(banks = banks,
                    pool = pool,
                    generators = [Beat, GhostEcho],
                    tracks = tracks,
                    tags = tags,
                    terms = terms).cmdloop()
    except RuntimeError as error:
        logging.error(str(error))
