### short

- track should be first arg in model.randomise()

### medium

- density and temperature variations

### SV

- refactor sample_cutoff as simply cutoff

### features

- track muting, freezing
- track mixing levels
- tagging and purging

### thoughts

- replace levels with mutes?
  - they are the same thing, int vs boolean
  - you would still need a class to represent mute state

### gists

- 303 slide
- echo freeze
- polly vocals + vocoder
- autotune
- resampling
- pico play modes
- granular
- kicker

### done

- move sample cutoff parameter up to cli
- sample cutoff cli variable
- add back `all` output
- revert randomise_xxx as mutate_xxx
- only export individual tracks
- simplify track naming
- refactor cli do_mutate as do_randomise
- sv 0.3.19
- merge randomiser and arranger back into base cli to form single unified cli again 
- split existing arrangement code into arrange random (no args) and arrange custom (hex arg)
- model tests needs to cover SynthTrack class and mutate() methods
- run tests
- remove everything in tmp
- start cli
- check banks initialised
- randomise params
- exit
- check git saved
- restart
- check git loaded
- clone col
- mutate samples
- clone col
- mutate seeds
- exit
- load arranger
- arrange
- export

- add basic arranger
- add back hex support
- refactor tracks.randomise to call track.randomise
- call randomise_params polymorphically
- add new randomise which calls instance
- rename randomise as randomise_params
- cli checkout 
- to_json needs to deepcopy
- base cli
- rename cli as randomiser
- simplify tracks init
- expand Tracks.__init__()
- expand Tracks.randomise() 
- add track type
- add back mutate() nomenclature to model
- refactor test names to explicitly reference sample track
- randomise to return dict
- abstracy track cloning 
- abstract track rendering
- separate synth, sample tracks
- add back randomise, mutate nomenclature
- add clean check
- simplify tag mapping
- clean doesn't need user input
- abstract tracks to yaml
- pass machine name from cli
- pass generators from cli to model
- remove arranging
- remove hex support


