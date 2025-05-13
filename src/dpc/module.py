from __future__ import annotations
import typing as t
import os

from .IO.script import ScriptDecoratable

if t.TYPE_CHECKING:
    from .packdsl import PackDSL

class Module(ScriptDecoratable):
    
    parent: PackDSL | Module
    _name: str
    
    def __init__(self, parent: PackDSL | Module, name: str):
        self.parent = parent
        self._name = name
    
    @property
    def _pack_reference(self) -> PackDSL:
        return self.parent._pack_reference
    
    @property
    def _file_root(self) -> str:
        return os.path.join(self.parent._file_root, self._name) 