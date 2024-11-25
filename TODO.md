### short

- add back mutate() nomenclature to model

- add track type
- initialise track based on track type

- base cli
- rename cli as randomiser
- new arranger cli

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


