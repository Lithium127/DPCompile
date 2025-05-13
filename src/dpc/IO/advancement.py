from __future__ import annotations
import typing as t

import json

from .jsonfile import JsonFile


class Advancement(JsonFile):
    """Represents an advancement that the player
    can achieve within the game."""
    
    def __init__(self, name):
        super().__init__(name)
    
    def render(self):
        return json.dumps({"nothing":"nothing"})