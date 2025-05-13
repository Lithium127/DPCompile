"""Module that contains all datatypes used in a datapack, usually representing
a concept from within the game and abstracting other information to simplify
the process of evaluating conditional information."""
from __future__ import annotations
import typing as t
from abc import ABC, abstractmethod
from enum import Enum


class MinecraftType(ABC):
    """The base type used for all datatypes that represent
    information from the game. Any implemented datatypes are
    required to override the `to_command_str()` method.
    
    Note that this is an abstract class provided by the `abc`
    module, meaning any subclasses that are created must never
    call `super().__init__()` and the init method raises a
    `NotImplementedError` currently."""
    
    def __init__(self):
        raise NotImplementedError("Cannot instance an abstract class")
    
    @abstractmethod
    def to_command_str(self) -> str:
        """Return the string representation used in commands."""
        pass
    
    # TODO: Make a comparison type that returns whenever an instance of a type is compared


from .literal import Literal

def ensure_mctype(val: t.Any) -> MinecraftType:
    """Ensures that a value is a valid command 
    datatype. If the value is not of correct type
    it is added to a `Literal` datatype and returned

    Args:
        val (Any): A given value that need be checked.

    Returns:
        MinecraftType: The validated value
    """
    if isinstance(val, MinecraftType):
        return val
    return Literal(val)

# Non-MinecraftType classes
from .version import Version as Version
from .version import Versionable as Versionable
from .version import VersionError as VersionError
from .version import VersionRange as VersionRange

# Other pack imports
from .block import Block as Block
from .block import Blocks as Blocks
from .position import Position as Position
from .textelement import TextElement as TextElement
from .textelement import to_textelement as to_textelement
from .selector import Selector as Selector
from .selector import ensure_selector as ensure_selector

# Command dependent datatypes
from .scoreboard import Scoreboard as Scoreboard