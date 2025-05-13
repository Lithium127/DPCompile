from __future__ import annotations
import typing as t

from enum import Enum

from . import MinecraftType

class SelectorGroup(Enum):
    EVERYTHING = "e"
    """`[SelectorGroup]`: Target every loaded, ticking entity within the world, including players"""
    ALL = "a"
    """`[SelectorGroup]`: Target all players currently within the world"""
    RANDOM = "r"
    """`[SelectorGroup]`: Target a random player currently within the world"""
    NEAREST = "p"
    """`[SelectorGroup]`: Target the player nearest to the location the current command executed at"""
    CURRENT = "s"
    """`[SelectorGroup]`: Target the currently selected entity that the current command is referencing"""

class Selector(MinecraftType):
    
    GROUP = SelectorGroup
    """An enum containing all available groups that a selector can reference."""
    
    _selector: str
    conditions: dict[str, t.Any]
    
    def __init__(self, group: str, conditions: dict[str, t.Any] = {}):
        self.selector = group
        self.conditions = conditions
    
    @classmethod
    def ALL(cls, **kwargs) -> Selector:
        """Creates a selector object that targets
        all players. Synonomous with `'@a'`

        Returns:
            Selector: Generated selector
        """
        instance = super().__new__(cls)
        cls.__init__(instance, SelectorGroup.ALL, **kwargs)
        return instance
    
    @property
    def selector(self) -> str:
        return self._selector
    
    @selector.setter
    def selector(self, value: str) -> None:
        self._selector = value if isinstance(value, str) else value.value
    
    def to_command_str(self):
        conditions_list = [f"{key}={value}" for key, value in self.conditions.items()]
        return f"@{self._selector}" + ("[" + ",".join(conditions_list) + "]" if len(conditions_list) > 0 else "")

def ensure_selector(target: str | Selector) -> Selector:
    """Ensures that a given argument is a selector by
    converting single character string values into
    a selection

    Args:
        target (str | Selector): The value to validate

    Returns:
        Selector: The selector instance
    """
    if isinstance(target, Selector):
        return target
    return Selector(target)