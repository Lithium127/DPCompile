from __future__ import annotations
import typing as t

from .packfile import PackFile

class NBTFile(PackFile):

    content: dict[str, t.Any]

    def __init__(self, name):
        super().__init__(name)
    
    def render(self):
        return ""