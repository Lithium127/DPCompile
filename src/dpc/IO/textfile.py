from __future__ import annotations
import typing as t

from .packfile import PackFile

class TextFile(PackFile):
    """Represents a pure tetx"""
    
    content: str
    
    def __init__(self, name: str, content: str):
        """Creates a representation of a pure text file
        within the datapack, commonly used to add a
        readme.md file within the pack.

        Args:
            pack (PackDSL): The pack that parents this file
            name (str): _description_
            content (str): _description_
        """
        super().__init__(name)
        self.content = content
    
    def render(self):
        return self.content