from sv.utils.export import export_wav

from euclid09.cli.levels import Levels
from euclid09.cli.plugins.detroit import SoundPlugin
from euclid09.colours import Colours
from euclid09.generators import Beat, GhostEcho
from euclid09.git import Git
from euclid09.model import Project
from euclid09.parse import parse_line

from functools import wraps

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
    @wraps(fn)
    def wrapped(self, *args, **kwargs):
        try:
            if self.git.is_empty():
                raise RuntimeError("Please create a commit first")
            return fn(self, *args, **kwargs)
        except RuntimeError as error:            
            logging.warning(str(error))
    return wrapped

def commit_and_render(fn):
    @wraps(fn)
    def wrapped(self, *args, **kwargs):
        project = fn(self, *args, **kwargs)
        colours = Colours.randomise(tracks = self.tracks,
                                    patches = project.patches)
        container = project.render(banks = self.sound_plugin.banks,
                                   generators = self.generators,
                                   colours = colours,
                                   bpm = self.bpm,
                                   tpb = self.tpb,
                                   n_ticks = self.n_ticks)
        commit_id = self.git.commit(project)
        if not os.path.exists("tmp/sunvox"):
            os.makedirs("tmp/sunvox")
        container.write_project(f"tmp/sunvox/{commit_id}.sunvox")
    return wrapped
           
class Euclid09CLI(cmd.Cmd):

    prompt = ">>> "
    intro = "Welcome to the Euclid09 CLI ;)"

    def __init__(self, tracks, sound_plugin, generators, bpm, tpb, n_patches, n_ticks):
        super().__init__()
        self.tracks = tracks
        self.sound_plugin = sound_plugin
        self.generators = generators                
        self.bpm = bpm
        self.tpb = tpb
        self.n_patches = n_patches
        self.n_ticks = n_ticks
        self.git = Git("tmp/git")

    def preloop(self):
        logging.info("Fetching commits ...")
        self.git.fetch()
        logging.info(self.sound_plugin.show_tags())

    ### tags
    
    def do_randomise_tags(self, _):
        """Randomise the tags associated with tracks."""
        self.sound_plugin.randomise_tags()
        logging.info(self.sound_plugin.show_tags())
        
    def do_show_tags(self, _):
        logging.info(self.sound_plugin.show_tags())

    def do_reset_tags(self, _):
        self.sound_plugin.reset_tags(self.tracks)
        logging.info(self.sound_plugin.show_tags())

    ### patch operations

    @commit_and_render
    def do_randomise_project(self, _):
        sounds = self.sound_plugin.filter_sounds(self.tracks)
        """Create a randomised project with patches."""
        return Project.randomise(tracks=self.tracks,
                                 sounds=sounds,
                                 n_patches=self.n_patches,
                                 n_sounds = 2)
                                 
    @assert_head
    @parse_line([{"name": "I", "type": "hexstr"}])
    @commit_and_render
    def do_select_patches(self, I):
        """Select specific patches from the latest project by index."""
        roots = self.git.head.content.patches
        project = Project()
        for i in I:
            patch = roots[i].clone()
            project.patches.append(patch)
        project.freeze_patches(len(I))
        return project

    @assert_head
    @parse_line([{"name": "I", "type": "hexstr"}])
    @commit_and_render
    def do_clone_patches(self, I):
        """Clone selected patches to create new ones."""
        roots = self.git.head.content.patches
        project = Project()
        for i in range(self.n_patches):
            j = I[i % len(I)]
            patch = roots[j].clone()
            project.patches.append(patch)
        project.freeze_patches(len(I))
        return project
            
    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_mutate_sounds(self, n):
        """Mutate the sounds of unfrozen patches in the project."""
        sounds = self.sound_plugin.filter_sounds(self.tracks)
        project = self.git.head.content.clone()
        for patch in project.patches:
            if not patch.frozen:
                for _ in range(n):
                    patch.mutate_attr(attr="sounds",
                                      filter_fn=lambda x: True,
                                      sounds=sounds)
        return project

    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_mutate_patterns(self, n):
        """Mutate the patterns of unfrozen patches in the project."""
        project = self.git.head.content.clone()
        for patch in project.patches:
            if not patch.frozen:
                for _ in range(n):
                    patch.mutate_attr(attr="pattern",
                                      filter_fn=lambda x: True)
        return project

    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_mutate_seeds(self, n):
        """Mutate the seeds of unfrozen patches in the project."""
        project = self.git.head.content.clone()
        for patch in project.patches:
            if not patch.frozen:
                for _ in range(n):
                    patch.mutate_attr(attr="seeds",
                                      filter_fn=lambda x: True)
        return project

    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_mutate_density(self, n):
        """Mutate the density values of unfrozen patches in the project."""
        project = self.git.head.content.clone()
        for patch in project.patches:
            if not patch.frozen:
                for _ in range(n):
                    patch.mutate_attr(attr="density",
                                      filter_fn=lambda x: True)
        return project

    @assert_head
    @parse_line([{"name": "n", "type": "int"}])
    @commit_and_render
    def do_mutate_temperature(self, n):
        """Mutate the temperature values of unfrozen patches in the project."""
        project = self.git.head.content.clone()
        for patch in project.patches:
            if not patch.frozen:
                for _ in range(n):
                    patch.mutate_attr(attr="temperature",
                                      filter_fn=lambda x: True)
        return project
        
    ### export
    
    @assert_head
    def do_export_stems(self, _):
        """Export the current project as stems in a zip file."""
        if not os.path.exists("tmp/wav"):
            os.makedirs("tmp/wav")
        commit_id = self.git.head.commit_id
        zip_name = f"tmp/wav/{commit_id.slug}-{self.bpm}-{self.n_ticks}.zip"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            levels = [Levels(self.tracks)]
            for track in self.tracks:
                levels.append(Levels(self.tracks).solo(track["name"]))
            project = self.git.head.content
            for levels_ in levels:
                container = project.render(banks=self.sound_plugin.banks,
                                           generators=self.generators,
                                           levels=levels_,
                                           bpm=self.bpm,
                                           tpb=self.tpb,
                                           n_ticks=self.n_ticks)
                sv_project = container.render_project()
                wav_io = export_wav(project=sv_project)
                wav_name = f"{commit_id.short_name}-{levels_.short_code}.wav"
                logging.info(wav_name)
                zip_file.writestr(wav_name, wav_io.getvalue())

    ### git
    
    def do_git_head(self, _):
        """Display the current HEAD commit."""
        if self.git.is_empty():
            logging.warning("Git has no commits")
        else:
            logging.info(f"HEAD is {self.git.head.commit_id}")

    def do_git_log(self, _):
        """Display the list of all commits."""
        for commit in self.git.commits:
            logging.info(commit.commit_id)

    def do_git_checkout(self, commit_id):
        """Checkout a specific commit by its ID."""
        self.git.checkout(commit_id)
        
    def do_git_undo(self, _):
        """Undo the most recent commit."""
        self.git.undo()

    def do_git_redo(self, _):
        """Redo the last undone commit."""
        self.git.redo()

    ### project management

    def do_clean_projects(self, _):
        """Clean all temporary project directories."""
        while True:
            answer = input(f"Are you sure ?: ")
            if answer == "y":
                for dir_name in ["tmp/git", "tmp/sunvox"]:
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
        """Exit the CLI."""
        return self.do_quit(None)

    def do_quit(self, _):
        """Exit the CLI."""
        logging.info("Exiting ..")
        return True

def parse_args(default_bpm = 120,
               default_tpb = 1,
               default_n_ticks = 16,
               default_n_patches = 16,
               default_cutoff = 250): # 2 * 2000 / 16 == two ticks @ 120 bpm
    parser = argparse.ArgumentParser(description="Run Euclid09CLI with specified parameters.")
    parser.add_argument(
        "--bpm",
        type=int,
        default=default_bpm,
        help=f"An integer > 0 specifying the beats per minute (default: {default_bpm})."
    )
    parser.add_argument(
        "--tpb",
        type=int,
        default=default_tpb,
        help=f"An integer > 0 specifying the number of ticks per beat (default: {default_tpb})."
    )
    parser.add_argument(
        "--n_ticks",
        type=int,
        default=default_n_ticks,
        help=f"An integer > 0 specifying the number of ticks (default: {default_n_ticks})."
    )
    parser.add_argument(
        "--n_patches",
        type=int,
        default=default_n_patches,
        help=f"An integer > 0 specifying the number of patches (default: {default_n_patches})."
    )
    parser.add_argument(
        "--cutoff",
        type=float,
        default=default_cutoff,
        help=f"A float > 0 specifying the cutoff value (default: {default_cutoff})."
    )  
    args = parser.parse_args()
    if args.bpm <= 0:
        parser.error("bpm must be an integer greater than 0.")
    if args.tpb <= 0:
        parser.error("tpb must be an integer greater than 0.")
    if args.n_ticks <= 0:
        parser.error("n_ticks must be an integer greater than 0.")
    if args.n_patches <= 0:
        parser.error("n_patches must be an integer greater than 0.")
    if args.cutoff <= 0:
        parser.error("cutoff must be a float greater than 0.")
    return args

if __name__ == "__main__":
    try:
        args = parse_args()
        tracks = load_yaml("tracks.yaml")
        sound_plugin = SoundPlugin(tracks = tracks,
                                   cutoff = args.cutoff)
        Euclid09CLI(tracks = tracks,
                    sound_plugin = sound_plugin,
                    generators = [Beat, GhostEcho],
                    bpm = args.bpm,
                    tpb = args.tpb,
                    n_ticks = args.n_ticks,
                    n_patches = args.n_patches).cmdloop()                
    except ValueError as error:
        logging.error(str(error))
    except RuntimeError as error:
        logging.error(str(error))



