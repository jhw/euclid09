from sv.banks import SVBanks
from sv.utils.banks import init_banks
from sv.utils.export import export_wav

from euclid09.cli.colours import Colours
from euclid09.cli.levels import Levels
from euclid09.cli.tags import Tags
from euclid09.generators import Beat, GhostEcho
from euclid09.git import Git
from euclid09.model import Project
from euclid09.parse import parse_line

import argparse
import cmd
import logging
import os
import sys
import yaml
import zipfile

logging.basicConfig(stream = sys.stdout,
                    level = logging.INFO,
                    format = "%(levelname)s: %(message)s")

def load_yaml(file_name):
    return yaml.safe_load(open("/".join(__file__.split("/")[:-1] + [file_name])).read())

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
        project, freeze = fn(self, *args, **kwargs)
        if freeze != None:
            self.freeze = freeze
        levels = Levels(self.tracks)
        colours = Colours.randomise(tracks = self.tracks,
                                    patches = project.patches)
        container = project.render(banks = self.banks,
                                   generators = self.generators,
                                   levels = levels,
                                   colours = colours)
        commit_id = self.git.commit(project)
        if not os.path.exists("tmp/sunvox"):
            os.makedirs("tmp/sunvox")
        container.write_project(f"tmp/sunvox/{commit_id}.sunvox")
    return wrapped
                
class Euclid09CLI(cmd.Cmd):

    prompt = ">>> "
    intro = "Welcome to the euclid09 CLI ;)"
    
    def __init__(self, tracks, banks, pool, generators, tags, cutoff, n_patches):
        super().__init__()
        self.tracks = tracks
        self.banks = banks
        self.pool = pool
        self.generators = generators                
        self.tags = tags
        self.n_patches = n_patches
        self.cutoff = cutoff
        self.git = Git("tmp/git")
        self.freeze = 0

    def preloop(self):
        logging.info("Fetching commits ...")
        self.git.fetch()
        self.do_show_tags(None)

    def postloop(self):
        logging.info("Pushing commits ...")
        self.git.push()
    
    ### tags

    def do_show_tags(self, _):
        logging.info(", ".join([f"{k}={v}" for k, v in self.tags.items()]))
    
    def do_rand_tags(self, _):
        self.tags.randomise()
        self.do_show_tags(None)

    def do_reset_tags(self, _):
        self.tags = Tags(tracks = tracks, terms = self.tags.terms)
        self.do_show_tags(None)

    ### patch operations
    
    @commit_and_render
    def do_rand_project(self, _):
        return Project.randomise(tracks = self.tracks,
                                 pool = self.pool,
                                 tags = self.tags,
                                 cutoff = self.cutoff,
                                 n = self.n_patches), 0

    @assert_head
    @parse_line([{"name": "I", "type": "hexstr"}])
    @commit_and_render
    def do_select_patches(self, I):
        roots = self.git.head.content.patches
        project = Project()
        for i in I:
            patch = roots[i].clone()
            project.patches.append(patch)
        return project, len(I)

    @assert_head
    @parse_line([{"name": "I", "type": "hexstr"}])
    @commit_and_render
    def do_clone_patches(self, I):
        roots = self.git.head.content.patches
        project = Project()
        for i in range(self.n_patches):
            j = I[i % len(I)]
            patch = roots[j].clone()
            project.patches.append(patch)
        return project, len(I)

    
        
    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_rand_samples(self, n):
        project = self.git.head.content.clone()
        for patch in project.patches[self.freeze:]:
            for _ in range(n):
                patch.randomise_attr(attr = "samples",
                                     filter_fn = lambda x: True,
                                     pool = self.pool,
                                     tags  =self.tags)
        return project, None

    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_rand_pattern(self, n):
        project = self.git.head.content.clone()
        for patch in project.patches[self.freeze:]:
            for _ in range(n):
                patch.randomise_attr(attr = "pattern",
                                     filter_fn = lambda x: True)
        return project, None

    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_rand_seeds(self, n):
        project = self.git.head.content.clone()
        for patch in project.patches[self.freeze:]:
            for _ in range(n):
                patch.randomise_attr(attr = "seeds",
                                     filter_fn = lambda x: True)
        return project, None
        
    ### export
    
    @assert_head
    def do_export_stems(self, _):
        if not os.path.exists("tmp/wav"):
            os.makedirs("tmp/wav")
        commit_id = self.git.head.commit_id
        zip_name = f"tmp/wav/{commit_id.slug}.zip"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            levels = [Levels(self.tracks)]
            for track in self.tracks:
                levels.append(Levels(self.tracks).solo(track["name"]))
            project = self.git.head.content
            colours = Colours.randomise(tracks = self.tracks,
                                        patches = project.patches)
            for levels_ in levels:
                container = project.render(banks = self.banks,
                                           generators = self.generators,
                                           levels = levels_,
                                           colours = colours)
                sv_project = container.render_project()
                wav_io = export_wav(project = sv_project)
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

    def do_git_checkout(self, commit_id):
        self.git.checkout(commit_id)
            
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
                        logging.info(f"cleaning {dir_name}")
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

def parse_args(default_cutoff = 0.5,
               default_n_patches = 16,
               default_profile = "profiles/default.yaml"):
    parser = argparse.ArgumentParser(description="Run Euclid09CLI with specified parameters.")
    parser.add_argument(
        "--cutoff",
        type=float,
        default=default_cutoff,
        help=f"A float > 0 specifying the cutoff value (default: {default_cutoff})."
    )
    parser.add_argument(
        "--n_patches",
        type=int,
        default=default_n_patches,
        help=f"An integer > 0 specifying the number of patches (default: {default_n_patches})."
    )
    parser.add_argument(
        "--profile",
        type=str,
        default=default_profile,
        help=f"Path to the profile YAML file (default: {default_profile})."
    )
    args = parser.parse_args()
    if args.cutoff <= 0:
        parser.error("cutoff must be a float greater than 0.")
    if args.n_patches <= 0:
        parser.error("n_patches must be an integer greater than 0.")
    if not os.path.isfile(f"euclid09/cli/{args.profile}"):
        raise RuntimeError(f"The profile file '{args.profile}' does not exist.")
    return args

if __name__ == "__main__":
    try:
        args = parse_args()
        tracks = load_yaml(args.profile)
        banks = SVBanks.load_zip(cache_dir="banks")
        terms = load_yaml("terms.yaml")
        pool, _ = banks.spawn_pool(tag_patterns=terms)
        tags = Tags(tracks = tracks, terms = terms).validate().randomise()
        Euclid09CLI(tracks = tracks,
                    banks = banks,
                    pool = pool,
                    generators = [Beat, GhostEcho],
                    tags = tags,
                    cutoff = args.cutoff,
                    n_patches = args.n_patches).cmdloop()
    except RuntimeError as error:
        logging.error(str(error))

