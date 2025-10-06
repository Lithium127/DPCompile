from __future__ import annotations
import typing as t
from enum import Enum

from .mctype import MinecraftType


class _PositionMode(Enum):
    ABSOLUTE = "abs"
    """Interpret this position as absolute from the world center"""
    
    RELATIVE = "rel"
    """Interpret this position as a relative distance from a current entity"""
    
    ROTATION = "rot"
    """Interpret this position as relative to an entities viewport, 
    where the `Z` axis is parallel to the view direction"""

class Position(MinecraftType):
    """Represents a position in 3D space"""
    
    FLAG = _PositionMode
    """An enumeration of modes for a position instance"""
    
    _pos: tuple[int, int, int]
    _mode: str
    _type: float | int
    
    @t.overload
    def __init__(self, value: list[int] | tuple[int, int, int]) -> None: 
        """Creates a new position instance from an iterable containing
        coordinate information.
        
        The coordinate will default to absolute

        Args:
            value (list[int] | tuple[int, int, int]): The index information
        """
        ...
    
    @t.overload
    def __init__(self, value: list[int] | tuple[int, int, int], flag: t.Literal["abs", "rel", "rot"]) -> None: 
        """Creates a new position instance from an iterable containing
        coordinate information, and a flag from the `Position.FLAG` enum
        
        Flag must be:
            ["abs"] - Absolute position
            ["rel"] - Relative to entity, denoted with '~'
            ["rot"] - Relative to entity viewport, denoted with '^'

        Args:
            value (list[int] | tuple[int, int, int]): The position data
            flag (["abs", "rel", "rot"]): What mode this position will use
        """
        ...
    
    @t.overload
    def __init__(self, x: int, y: int, z: int) -> None:
        """Creates a new position instance from a set
        of integers that hold position data.
        
        The coordinate will default to absolute

        Args:
            x (int): The `X` position
            y (int): The `Y` position
            z (int): The `Z` position
        """
        ...
    
    @t.overload
    def __init__(self, x: int, y: int, z: int, flag: t.Literal["abs", "rel", "rot"]) -> None:
        """Creates a new position instance from a set
        of integers that hold position data, and a 
        flag from the `Position.FLAG` enum

        Flag must be:
            ["abs"] - Absolute position
            ["rel"] - Relative to entity, denoted with '~'
            ["rot"] - Relative to entity viewport, denoted with '^'
        
        Args:
            x (int): The `X` position
            y (int): The `Y` position
            z (int): The `Z` position
            flag (["abs", "rel", "rot"]): What mode this position will use
        """
        ...
    
    def __init__(self, *args):
        """Instances a new position, representing a single location in 3D space"""
        if len(args) == 1:
            pos = args[0]
            self.set_position(pos)
            self.mode = _PositionMode.ABSOLUTE
        elif len(args) == 2:
            pos, mode = args
            self.set_position(pos)
            self.mode = mode
        elif len(args) == 3:
            x, y, z = args
            self.set_position((x, y, z))
            self.mode = _PositionMode.ABSOLUTE
        elif len(args) == 4:
            x, y, z, mode = args
            self.set_position((x, y, z))
            self.mode = mode
    
    def __eq__(self, value):
        if not isinstance(value, Position):
            return False
        return (self._pos == value._pos)        
    
    def to_command_str(self):
        return super().to_command_str()
    
    def set_position(self, value: tuple[int | float, int | float, int | float], *, use_type: float | int | None = None) -> None:
        """Directly sets the position data for this instance. Updates this instances current type
        if required, which is interpreted from the first argument within the data tuple.

        Args:
            value (tuple[int, int, int]): The new position information.
            use_type (Literal[float, int] | None, optional): An override for type interpretation, 
                                                             all data fields within the data tuple 
                                                             are cast to this type or the type of 
                                                             the first argument. Defaults to None.
        """
        self._type = use_type or (float if isinstance(value[0], float) else int)
        self._pos = (self._type(value[0]), self._type(value[1]), self._type(value[2]))

    @property
    def mode(self) -> str:
        return self._mode
    
    @mode.setter
    def mode(self, value: str) -> None:
        if value not in _PositionMode:
            raise ValueError(f"Requested mode for position {self} not within PositionMode Enum")
    
    @property
    def is_block_pos(self) -> bool:
        """Returns true if this instance references a block in space, 
        meaning contained data is of type integer."""
        return (self._type == int)
    
    @property
    def x(self) -> int:
        return self._pos[0]
    
    @x.setter
    def x(self, value: int) -> None:
        self._pos = (value, self.y, self.z)
    
    @property
    def y(self) -> int:
        return self._pos[1]
    
    @y.setter
    def y(self, value: int) -> None:
        self._pos = (self.x, value, self.z)
    
    @property
    def z(self) -> int:
        return self._pos[2]
    
    @z.setter
    def z(self, value) -> None:
        self._pos = (self.x, self.y, value)
