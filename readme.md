# DPCompile
A program that seeks to eliminate pains with Minecraft Datapack development. This
program constructs a datapack from normal python building blocks, meaning anyone
can create a datapack if they have even a little experience with python.

## Decorator Based Syntax
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

## Pack Versioning
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

## Scoreboard management
PackDSL makes initializing and working with scoreboards easier, minimizing naming conflicts
by automatically attaching the namespace of the pack to the name of each scoreboard, meaning
your values won't be overwritten by a different pack.