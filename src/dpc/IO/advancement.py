from __future__ import annotations
import typing as t

import json

from .jsonfile import JsonFile
from ..datatypes.textelement import to_textelement

if t.TYPE_CHECKING:
    from ..datatypes.textelement import TextElement

class AdvancementTrigger():
    pass

class Advancement(JsonFile):
    """Represents an advancement that the player
    can achieve within the game."""

    icon: dict[str, str]
    frame: t.Literal["challenge", "goal", "task"]

    title: TextElement
    description: TextElement
    
    def __init__(self, name):
        super().__init__(name)
    
    def render(self):
        return json.dumps({"nothing":"nothing"})