### fixed and floating 30/11/21

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
