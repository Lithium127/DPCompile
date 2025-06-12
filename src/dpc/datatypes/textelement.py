from __future__ import annotations
import typing as t

from enum import Enum
import json

from . import MinecraftType

if t.TYPE_CHECKING:
    from .selector import Selector

class TextElement(MinecraftType):
    """Represents a JSON encoded text element that is parsable by minecraft commands"""
    
    _content: dict[str, str]
    
    def __init__(self, text: str | TextElement, color: str = None):
        if isinstance(text, TextElement):
            self._content = {}
            for key in text._content.keys():
                self._content[key] = text._content.get(key, "")
            return None
        self._content = {}
        self.text = text
        self.color = color
    
    @property
    def text(self) -> str:
        return self._content.get("text", "")
    
    @text.setter
    def text(self, value: str) -> None:
        self._content["text"] = value
    
    @property
    def color(self) -> str | None:
        """The attribute representing the color of the given text"""
        return self._content.get("color", None)
    
    @color.setter
    def color(self, value: str) -> None:
        # TODO: Review this method and see if there is a cleaner way to write this
        if value is None:
            return None
        if value in TextElement.Colors or "hex" in value:
            self._content["color"] = value.value if isinstance(value, Enum) else value
    
    def to_command_str(self):
        return json.dumps(self._content)

    class Colors(Enum):
        """An enum of all colors useable by text elements including hex values"""
        WHITE = "white"
        BLACK = "black"
        RED = "red"
        YELLOW = "yellow"
        ORANGE = "dark_yellow"
        
        @classmethod
        def hex(cls, value) -> str:
            """Converts a given hex value to a string
            parsable by commands."""
            if isinstance(value, int):
                value = hex(int)
            return f"hex({value})"

def to_textelement(value: str | MinecraftType) -> TextElement:
    """Convert a string to a JSON text element for command inputs"""
    if isinstance(value, TextElement):
        return value
    return TextElement(text=str(value))
