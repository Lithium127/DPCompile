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

# File IO
from .IO.jsonfile import JsonFile as JsonFile
from .IO.mcmeta import McMeta as McMeta
from .IO.packfile import PackFile as PackFile
from .IO.packfile import FileParentable as FileParentable
from .IO.script import Script as Script
from .IO.script import ScriptDecoratable as ScriptDecoratable
from .IO.tagtable import TagTable as TagTable
from .IO.textfile import TextFile as TextFile

# Templates
from .template import script as script
from .template import Template as Template
from .template import TemplateDecoratable as TemplateDecoratable
from .template import TemplateError as TemplateError

# Core Datatypes
from .datatypes.mctype import MinecraftType as MinecraftType
from .datatypes.mctype import ensure_mctype as ensure_mctype
from .datatypes.literal import Literal as Literal
from .datatypes.version import Version as Version
from .datatypes.version import Versionable as Versionable
from .datatypes.version import VersionRange as VersionRange
from .datatypes.scoreboard import ScoreCriteria as ScoreCriteria
from .datatypes.scoreboard import Scoreboard as Scoreboard
from .datatypes.scoreboard import ScoreboardClosure as ScoreboardClosure

# MinecraftType Datatypes
from .datatypes.block import Block as Block
from .datatypes.block import BlockState as BlockState
from .datatypes.block import BlockPredicate as BlockPredicate
from .datatypes.item import Item as Item
from .datatypes.item import ItemData as ItemData
from .datatypes.position import Position as Position
from .datatypes.textelement import TextElement as TextElement
from .datatypes.selector import Selector as Selector
from .datatypes.selector import ensure_selector as ensure_selector

# MinecraftType Enums
from .datatypes.enum.block_enum import Blocks as Blocks
from .datatypes.enum.item_enum import Items as Items

# Commands
from . import cmd as cmd