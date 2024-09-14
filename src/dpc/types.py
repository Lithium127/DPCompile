import typing as t
import os

NBTData = t.Union[dict]
Target = t.Union[
    str, 
    'Player',
    t.Literal[
        "@a",
        "@e",
        "@p",
        "@r",
        "@s",
    ]
]
ResourceLocation = t.Union[str, os.PathLike]
BlockTarget = t.Union[
    "BlockPosition",
    tuple[int, int, int],
    list[int],
    
]

class WorldPosition:
    ...


class BlockPosition:
    
    _position: tuple[int, int, int]
    _relative: bool
    
    def __init__(self, x: int, y: int, z: int, relative: bool = False) -> None:
        self._position = (x, y, z)
        self._relative = relative
    
    def __add__(self, value: 'BlockPosition') -> None:
        self._position = (self.x + value.x, self.y + value.y, self.z + value.z)
    
    def __sub__(self, value: 'BlockPosition') -> None:
        self._position = (self.x - value.x, self.y - value.y, self.z - value.z)
        
    @property
    def x(self) -> int:
        return self._position[0]
    
    @x.setter
    def x(self, value: int) -> None:
        self._position = (self.x + value, self.y, self.z)
    
    @property
    def y(self) -> int:
        return self._position[1]
    
    @y.setter
    def y(self, value: int) -> None:
        self._position = (self.x, self.y + value, self.z)
    
    @property
    def z(self) -> int:
        return self._position[2]
    
    @z.setter
    def z(self, value: int) -> None:
        self._position = (self.x, self.y, self.z + value)
    
    @property
    def cmd_str(self) -> str:
        return f"{'~' if self._relative else ''}{self.x} {'~' if self._relative else ''}{self.y} {'~' if self._relative else ''}{self.z}"

class UUID:
    
    _value: str
    
    def __init__(self, value: str | int) -> None:
        self._value = str(value)
    
    def __str__(self) -> str:
        return self._value


class Player:
    pass