### Overview

A sample- based Euclidian pattern generator, rendered using Sunvox and implemeneted with radiant-voices

### Usage

```
(env) jhw@Justins-Air euclid09 % python euclid09/cli.py
INFO: Fetching commits ... # <-- loads patches on startup
INFO: Fetched 2024-11-26-06-35-37-technical-bake.json 
Welcome to the euclid09 CLI ;)
>>> randomise_patches # <-- initialises a project with a load of random patches; go to tmp/sunvox to see the results
INFO: HEAD is 2024-11-26-06-29-10-angry-exchange
>>> clone_patch 0 # <-- select a patch you like
INFO: HEAD is 2024-11-26-06-29-28-popular-inflation
>>> mutate_samples 2 # <-- keep the basic pattern but change some samples
INFO: HEAD is 2024-11-26-06-29-36-party-kick
>>> clone_patch 3 # <-- select another patch you like
INFO: HEAD is 2024-11-26-06-29-40-outside-map
>>> mutate_seeds 2 # <-- change the random seeds
INFO: HEAD is 2024-11-26-06-29-46-long-service
>>> show_tags # <-- inspect the tag groups from whence the samples come
INFO: clap: clap
hat: hat
kick: kick

>>> randomise_tags # <-- randomise the sample tag groups
INFO: clap: stab
hat: noise
kick: snare

>>> clone_patch 0 # <-- select another patch
INFO: HEAD is 2024-11-26-06-30-20-master-leading
>>> mutate_samples 2 # <-- randomise samples again
INFO: HEAD is 2024-11-26-06-30-29-big-singer
>>> git_undo # <-- don't like any of them; go back
INFO: HEAD is now at 2024-11-26-06-30-20-master-leading
>>> mutate_samples 2 # <-- re- randomise samples
INFO: HEAD is 2024-11-26-06-30-52-empty-nail
>>> randomise_arrangement 0123456789abcdef # <-- randomises arrangements based on hex input of patches you like (this still needs a lot of work to be useful)
INFO: HEAD is 2024-11-26-06-37-14-pretty-program
>>> export_stems # <-- export to wav, including all solos and mutes
SOUND: sundog_sound_deinit() begin
SOUND: sundog_sound_deinit() end
Max memory used: 4594693
Not freed: 4533897
MEMORY CLEANUP: 3712, 984, 2800, 6144, 160, 16, 3112, 4096, 512, 3528, 3528, 65536, 65536, 112, 4096, 5144, 112, 8192, 78336, 8, 256, 768, 3072, 96, 128, 96, 256, 96, 128, 96, 256, 96, 128, 96, 256, 96, 128, 96, 256, 96, 128, 96, 256, 96, 128, 96, 256, 96, 128, 96, 256, 96, 128, 96, 256, 96, 128, 96, 256, 96, 128, 96, 256, 96...
INFO: emp-nai-kch.wav
{...}
>>> exit
INFO: Exiting ..
INFO: Pushing commits ... # <-- saves new patches on shutdown
INFO: Pushed 2024-11-26-06-35-37-technical-bake.json
```



