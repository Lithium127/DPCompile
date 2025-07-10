# DPCompile
A program that seeks to eliminate pains with Minecraft Datapack development. This
program constructs a datapack from normal python building blocks, meaning anyone
can create a datapack if they have even a little experience with python.

> #### Work in Progress
> This project is still in development and is not yet available for public use. To see how to contribute to this project see the [contributing](#contributing) section


## Features

### Decorator Based Syntax
To keep in the python way, this library leverages decorators to attach functions that generate
the content of each script. This allows for multiple scripts to be created within the same
python program, or even the entire datapack if need be.

```python
with PackDSL() as pack:
    @pack.mcfn(sort='load')
    def load():
        Scoreboard('score').reset()
```
Do more with datapacks with even less code, no boilerplate or switching between files, scripts
are managed audomatically be the pack, when the pack context exits, the files get built.

### Pack Meta Management
`DPCompile` manages all aspects of pack creation, including what meta files are required and what they need to reference.
Meaning less time is spent on determining where files shoud go.

### Pack Versioning
Versioning datapacks has always been a nightmare, with commands inconsistently changing 
between versions that shouldn't be all that different, DPCompile holds a registry of
patches to avoid versioning conflicts, and makes the version accesible at build time,
meaning packs can perform the same operations on different versions of the game

```python
with PackDSL(..., version="1.21.4") as pack:
    @pack.mcfn(sort = "load")
    def display_version():
        cmd.Log.info(f"Pack loaded, version {pack.version}")
        # Logs "Pack loaded, version 1.21.4"
```

### Scoreboard management
PackDSL makes initializing and working with scoreboards easier, minimizing naming conflicts
by automatically attaching the namespace of the pack to the name of each scoreboard, meaning values won't be overwritten by a different pack.

This means that all scoreboard are accessable throughout every aspect
of a pack, removing the need to import lists of arbitrary scoreboards while enabling useful features within the DSL

```python
with PackDSL(...) as pack:
    # Criteria can be set from outside a script
    Scoreboard("health", criteria = ScoreCriteria.health())

    @pack.mcfn()
    def log_scoreboards():
        # References the same scoreboard as above
        cmd.Log.info(Scoreboard("health").name())
    
    @pack.mcfn()
    def reset_scores():
        # Scoreboards will be automatically initialized
        # if they dont exist elsewhere
        Scoreboard("is_hit").reset()
```


### Command Masking
`DPCompile` allows for commands and scripts to be marked as `dev_only` during development, and then for those commands to be removed from the pack when building for production.
```python
with PackDSL(..., dev = False) as pack:

    # This script only appears when development mode is on
    @pack.mcfn(dev = True)
    def show_debug_info():
        cmd.Log.info(f"Loaded scoreboards: {Scoreboard('is_sneaking').name()}")
    
    ...
    @pack.mcfn()
    def weapon_ability():
        Scoreboard('hits_combo').increment(1)
        # The Log command removed for production
        cmd.Log.info("Hit registered")
        # Commands can be marked as dev as well
        cmd.Command("say test", dev = True)
```

## Contributing
Thus far this project has been managed by a single person, however this project is free for anyone to make changes to or improve.


Potentual updates:
- replace vector class with named tuple and set of functions to operate
- - use static caching to store function constants via expensive functions

- - limit number of hashs that occur each loop
