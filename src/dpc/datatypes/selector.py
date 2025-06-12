from __future__ import annotations
import typing as t

from enum import Enum

from . import MinecraftType


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


from .scoreboard import Scoreboard

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
    """Representation of a selection of entities within the minecraft world.
    Selectors can be filtered by a conditions list to limit the number of
    entities selected.
    
    To see possible options for selectors, look at the `SelectorGroup` enum or
    use the class methods shortcuts.
    
    """
    
    GROUP = SelectorGroup
    """An enum containing all available groups that a selector can reference."""
    
    _selector: str
    conditions: dict[str, t.Any]
    
    def __init__(self, group: str, conditions: dict[str, t.Any] = {}):
        self.selector = group
        self.conditions = conditions
    
    
    @classmethod
    def EVERYTHING(cls, **kwargs) -> Selector:
        """Creates a selector object that targets
        all loaded entities within the world. 
        Synonomous with `'@e'`

        Returns:
            Selector: Generated selector
        """
        instance = super().__new__(cls)
        cls.__init__(instance, SelectorGroup.EVERYTHING, **kwargs)
        return instance
    
    
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
    
    
    @classmethod
    def RANDOM(cls, **kwargs) -> Selector:
        """Creates a selector object that targets
        a random player. Synonomous with `'@r'`

        Returns:
            Selector: Generated selector
        """
        instance = super().__new__(cls)
        cls.__init__(instance, SelectorGroup.RANDOM, **kwargs)
        return instance
    
    
    @classmethod
    def NEAREST(cls, **kwargs) -> Selector:
        """Creates a selector object that targets
        the nearest player. Synonomous with `'@p'`

        Returns:
            Selector: Generated selector
        """
        instance = super().__new__(cls)
        cls.__init__(instance, SelectorGroup.NEAREST, **kwargs)
        return instance
    
    
    @classmethod
    def CURRENT(cls, **kwargs) -> Selector:
        """Creates a selector object that targets
        the current player. Synonomous with `'@s'`

        Returns:
            Selector: Generated selector
        """
        instance = super().__new__(cls)
        cls.__init__(instance, SelectorGroup.CURRENT, **kwargs)
        return instance
    
    
    def if_score(self, score: str | Scoreboard, value, *, operator: t.Literal[">", "<"] | None = None) -> Selector:
        score = score if isinstance(score, Scoreboard) else Scoreboard(score)
        if not "scores" in self.conditions:
            self.conditions["scores"] = []
        self.conditions["scores"].append(f"{score.name()}={'..' if operator == '<' else ''}{value}{'..' if operator == '>' else ''}")
        return self
    
    
    def scoreboard(self, title: str) -> Scoreboard:
        # TODO: Scoreboards need a method to have a default selector passed or otherwise set.
        return Scoreboard()
    
    
    @property
    def selector(self) -> str:
        return self._selector
    
    @selector.setter
    def selector(self, value: str) -> None:
        self._selector = value if isinstance(value, str) else value.value
    
    
    def _build_condition_list(self) -> list[str]:
        conditions = []
        for key, value in self.conditions.items():
            if isinstance(value, list):
                value = "{" + ",".join(value) + "}"
            conditions.append(f"{key}={value}")
        return conditions
    
    
    def to_command_str(self):
        conditions_list = self._build_condition_list()
        return f"@{self._selector}" + ("[" + ",".join(conditions_list) + "]" if len(conditions_list) > 0 else "")
    