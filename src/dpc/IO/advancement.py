from __future__ import annotations
import typing as t

import json
import inspect

from .jsonfile import JsonFile
from ..datatypes.textelement import to_textelement

if t.TYPE_CHECKING:
    from ..datatypes.textelement import TextElement
    from ..datatypes.block import Block

class AdvancementTrigger():
    pass

class Advancement(JsonFile):
    """Represents an advancement that the player
    can achieve within the game."""

    _icon: dict[str, str]
    frame: t.Literal["challenge", "goal", "task"]
    name: str

    title: TextElement
    description: TextElement | None
    
    def __init__(self, name):
        super().__init__(name)
    
    def render(self):
        return json.dumps({"nothing":"nothing"})
    
    @property
    def icon(self) -> dict[str, str]:
        return self._icon
    
    @icon.setter
    def icon(self, val: Block) -> None:
        # This needs to work with items
        self._icon = {"item" : val.to_command_str(), "nbt" : val.tags}


def mc_advancement(name: str = None, desc: str | TextElement = None):
    """System for generating advancement from
    functions that modify an instances content.

    ```python
    @mc_advancement()
    def <advancement_name>(adv) -> None:
        \"\"\"<advancement_description>\"\"\"
        adv.add_triggers("tick", "something else")
        adv.icon = Blocks.STONE # Convert block to icon

    ```

    """

    def inner(func: callable):
        instance = Advancement.__new__(Advancement)

        # Set pre-determined advancement information
        instance.name = name or func.__name__
        instance.description = desc or to_textelement(func.__doc__)

        # Optionally generate content
        content = func(instance)
        return instance
    return inner