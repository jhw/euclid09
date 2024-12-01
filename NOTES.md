### polymorphic machines 01/12/24

- instead of profiles you want cli to select randomly from a list of machines
- probably highly weighted towards detroit sampler
- but including sv drum / tokyo
- and maybe including a simplified version of berlin which just plays a single note, where variation could come from changing note, changing note length or changing filter level
- how would you incorporate these options within the context of the existing beats machine interface?

### fixed and floating 30/11/24

- instead of patches you have fixed and floating, and concatenate them together for rendering
- rand_patches randomises floating and clears fixed
- select_patch inserts into fixed and fills float with copies
- possibly if fixed > floating them float picks are randomised
- rand_xxx where xxx != patches just randomises the float side
- but you probably need a new PatchCommit class to wrap fixed and floating Patches

### tagging and purging xx/11/24

- by default patches are just saved with timestamp, but all are saved to sunvox
- you have to call a tag() method for it to create a new commit, with a name
- prune() removed all non- tagged commits and maybe non- tagged sunvox files also
- only tagged versions are persisted by git
