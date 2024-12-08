### short [01-tbp-and-240-bpm]

- add tbp cli variable
- pass tbp to project rendering
- project to multiply bpm and n_ticks by tpb during render
- pass tbp to track to be included as part of machine env
- add tbp to generator kwargs
- check tbp when rendering

### medium

- merge tracks
- fix failing model tests
- add generator support for returning trig length

### features

- ability to vary cli cutoff/density/temperature
- optional s3 bank loading
- sample fx

### thoughts

- rename export_stems as export_wav?
  - no as then conflicts with export_wav import
- cli test?
  - seems a bridge too far
- track freezing?
  - not clear what it achieves

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

- add profile args for bpm, n_ticks
- move bpm from model to cli
- export bpm as part of stem name
- cli help descriptions
- refactor model mutation tests as they seem to focus on density and temperature
- tests failing due to density and temperature mutations
- refactor seeds.sample as seeds.sound
- add cutoff to samples
- add shuffle temperature, shuffle density
- mutate pattern needs to switch tracks or otherwise change densities
- tests for cli levels and tags
- rename randomise_attr as mutate_attr
- persist json patches after every commit
- tests for patch frozen attr
- freeze needs to be part of project
- mutate colours within range
- add colours test
- model to use default Levels
- rename TrackBase as SynthTrack
- export should not require colours 
- clean up tmp colours stuff in tests
- why does shuffle_sound require pool and tags to be passed? 
  - shouldn't machine be initialised with a large number of samples and these then randomised?  
- try and abstract pool/tag/cutoff stuff from model to cli
- continue replacement of model pool/tag/cutoff with **kwargs
- couldn't Class.randomise take kwargs not pool and tag?
- refactor SynthTrack/SampleTrack as BaseTrack, DetroitTrack
- refactor samples as sounds
- git operations should reset freeze
- remove profiles and rename default yaml as machines 
- rename default profile as detroit
- split select_patches into separate select, fill operations
- freeze integer
- rand_patches to clear fixed and randomise floating
- select patches to copy selected into fixed and clear floating
- fill patches to copy fixed into floating
- rand xxx to randomise floating
- is select cols doubling the number of patches?
- randomise tags on startup
- protection against track not being present in tags
- convert terms to class
- replace terms class with tags class
- abstract and test colours
- add colour class
- map kick/clap/hat to rgb
- abstract colours code inside class
- rename mod|pat_colours as machine|patch_colours
- move patch colour definition into cli
- add module colour nesting
- move module colour definition into cli
- test for new project class
- replace initialisation of empty lists
- test cli lifecycle
- replace refs to patches with project
- new project class w/ patches attr, copying patch w/ tracks
- randomise patch colours
- randomise module colours
- upgrade to sv 0.3.22
- check machines can be instantiated polymorphically with **kwargs
- rename SVTrigGroup as SVMachineTrigs
- new select_patch based on arrange_custom
  - fills as well
- remove clone_col
- stop old mutate_ methods from preserving
- add back hex support
- rename randomise_ and mutate_ as rand_
- test model polymorphism
- refactor mutation so applied on per- track basis
- add mutation filter_fn
- replace track type with check to see if track class extends SVSamplerMachine
- cli to request profile on startup
- default cli args
- remove arranger
- use argsparse to accept values for cutoff and n_patches
- refactor cli sample_cutoff as simply cutoff
- rename tag_mapping in model test
- pass named args to track.randomise
- track should be first arg in model.randomise()
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


