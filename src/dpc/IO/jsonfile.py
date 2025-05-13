from __future__ import annotations

from .packfile import PackFile

# TODO: Make ABC meta, and implement the render function, requesting JSON files override a `get_content` method

class JsonFile(PackFile):
    """Represents a file with the """
    
    indent: int
    
    def __init__(self, name, *, indent: int = 4):
        super().__init__(name)
        self.extension = "json"
        self.indent = indent

    def write(self, path = None):
        return super().write(path)

    def render(self) -> dict | None:
        return None