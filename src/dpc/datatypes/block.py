from __future__ import annotations
import typing as t

from enum import Enum

from . import MinecraftType


class Block(MinecraftType):
    
    id: int
    namespace: str
    name: str
    display_name: str
    hardness: float
    
    tags: dict[str, t.Any]
    
    def __init__(self, 
                 name: str, 
                 namespace: str | None = None, 
                 *, 
                 id: int = None, 
                 display_name: str = None, 
                 hardness: float = None,
                 tags: dict[str, t.Any] | None = None
                 ) -> None:
        """Represents a single block type within the game. Without a position or other
        game-based information. The namespace defaults to 'minecraft', however can be
        passed in the constructor. If the namespace is not overriden but the name
        argument contains a ':' character (ex: `'arbitrary:blockname'`), the namespace
        is interpreted from the first part of the name.

        Args:
            name (str): The name of the block, can include the namespace which will be
                        used as long as a namespace is not passed
            namespace (str | None, optional): The namespace for this block, interpreted 
                                              from name and will default to 'minecraft' 
                                              is none is given. Defaults to None.
            tags (dict[str, t.Any] | None, optional): The given block tags for this block 
                                                      as a dict containing `tag:value`. 
                                                      Defaults to None.
        """
        if (":" in name) and (namespace is None):
            namespace, name = name.split(":")[:2]
        self.name = name
        self.namespace = namespace or 'minecraft'
        self.display_name = display_name
        self.id = id
        self.hardness = hardness
        self.tags = tags or {}
    
    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self, value):
        if not isinstance(value, Block):
            return False
        return self.id == value.id
    
    def to_command_str(self):
        if len(self.tags.keys()) == 0:
            return f"{self.namespace}:{self.name}"
        tag_str = " ".join([f"{tag}={value}" for tag, value in self.tags.items()])
        return f"{self.namespace}:{self.name}[{tag_str}]"