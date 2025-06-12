"""A DSL for datapacks, adding object oriented programming to
a statically typed language.

The idea behind DPCompile is to move datapacks away from being single version,
and difficult to work with, requiring static typing and missing the idea of simple
variables.

DPCompile manages the entire process of generating datapacks behind the scenes while
keeping the door open to enable low-level operations. Meaning packs can be created
with as little code as possible.

# Getting Started
All packs start with the `PackDSL`, which must be opened in a context and manages
every aspect of the pack.

```python
from dpc import PackDSL

with PackDSL(<name>, <namespace>, ...) as pack:
    ...
```

To add functions to the datapack, just decorate with the `.mcfn()` decorator and
make calls to the cmd library, the PackDSL context will handle the creation of
scripts and the build call when the `with` statement is exited.

```python
from dpc import PackDSL, cmd, Script

with PackDSL(...) as pack:

    @pack.mcfn()
    def tick():
        cmd.Comment("This is a ticking function")
        
    # The Script instance can also be passed to the
    # function automatically, and the name of the
    # script can be overriden with an argument
    @pack.mcfn()
    def load(script: Script):
        cmd.Command("tellraw {'text' : 'Script: " + script.full_name + " loaded'}")
```

Managing metadata for required packs can also be performed here with access to the
PackDSL `meta` property, enabling required features or omitting features from other 
packs where needed. The PackDSL will manage the `pack.mcmeta` file at buildtime

```python
from dpc import PackDSL, cmd

with PackDSL(...) as pack:
    # Enable locator bar feature
    pack.meta.require_feature(
        pack.meta.FEATURES.LOCATOR
    )
```
"""
# TODO: Performance tracking for selectors and commands\
# TODO: Logging during build time.


from .packdsl import PackDSL as PackDSL
from .module import Module as Module
from .module import modulemethod as modulemethod

# File IO
from .IO.jsonfile import JsonFile as JsonFile
from .IO.mcmeta import McMeta as McMeta
from .IO.packfile import PackFile as PackFile
from .IO.packfile import FileParentable as FileParentable
from .IO.script import Script as Script
from .IO.script import ScriptDecoratable as ScriptDecoratable
from .IO.tagtable import TagTable as TagTable
from .IO.textfile import TextFile as TextFile

# Core Datatypes
from .datatypes import MinecraftType as MinecraftType
from .datatypes import ensure_mctype as ensure_mctype
from .datatypes import Literal as Literal
from .datatypes import Version as Version
from .datatypes import Versionable as Versionable
from .datatypes import VersionRange as VersionRange
from .datatypes import ScoreCriteria as ScoreCriteria
from .datatypes import Scoreboard as Scoreboard
from .datatypes import ScoreboardClosure as ScoreboardClosure

# MinecraftType Datatypes
from .datatypes import Block as Block
from .datatypes import Blocks as Blocks
from .datatypes import Position as Position
from .datatypes import TextElement as TextElement
from .datatypes import Selector as Selector
from .datatypes import ensure_selector as ensure_selector

# Commands
from . import cmd as cmd