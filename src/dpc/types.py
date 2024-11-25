import typing as t
import os

NBTData = t.Union[dict]

Selector = t.Literal["@a", "@e", "@p", "@r", "@s"]

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
    _relative: t.Literal["world", "entity", "rotation"]
    
    def __init__(self, x: int, y: int, z: int, relative: t.Literal["world", "entity", "rotation"] = "world") -> None:
        """Represents a position of a block in the world, can be relative to
        the world, an entity ('~') or an entity rotation ('^')

        Args:
            x (int): Block X position
            y (int): Block Y position
            z (int): Block Z position
            relative (["world", "entity", "rotation"], optional): What this position is relative to. Defaults to "world".
        """
        self._position = (x, y, z)
        self._relative = relative
        
    def __str__(self) -> str:
        return f"<BlockPosition ({self.x}, {self.y}, {self.z})>"
    
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
    def is_absolute(self) -> bool:
        """True when this position is relative to the world"""
        return (self._relative == "world")
    
    @property
    def cmd_str(self) -> str:
        relative = {
            "world" : '',
            "entity" : '~',
            "rotation" : '^'
        }[self._relative]
        return f"{relative}{self.x} {relative}{self.y} {relative}{self.z}"

class UUID:
    
    _value: str
    
    def __init__(self, value: str | int) -> None:
        self._value = str(value)
    
    def __str__(self) -> str:
        return self._value

class Swizzle:
    
    x: bool
    y: bool
    z: bool
    
    def __init__(self, dir: list[t.Literal["x","y","z"]]) -> None:
        self.x = "x" in dir
        self.y = "y" in dir
        self.z = "z" in dir
    
    def __call__(self) -> str:
        return self.value()
    
    def value(self) -> str:
        return f"{'x' if self.x else ''}{'y' if self.y else ''}{'z' if self.z else ''}"

class Biome:
    
    name: str
    namespace: str
    
    def __init__(self, name: str) -> None:
        name = name.split(":")
        self.name = name[0] if len(name) == 1 else name[2]
        self.namespace = name[0] if len(name) == 2 else "minecraft"
    
    def __str__(self) -> str:
        return f"{self.namespace}:{self.name}"