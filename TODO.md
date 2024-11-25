### short

- model tests needs to cover SynthTrack class and mutate() methods

### sv

- add beats interface with xxx_sound nomenclature (not xxx_sample)

- refactor fx sz parameter as global cutoff_ticks or similar

### medium

- refactor export muting to remove levels
  - render project without muted tracks 

- track muting, freezing
- track mixing levels
- tagging and purging

### thoughts

### gists

- 303 slide
- echo freeze
- sv drum
- polly vocals + vocoder
- autotune
- resampling
- pico play modes
- granular
- kicker

### done

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


