import typing as t
from .types import Selector

class EntityData(t.TypedDict):
    
    name: t.Required[str]
    
    def __init__(self) -> None:
        super(EntityData, self).__init__()

class Entity(object):
    
    _data: EntityData
    _value: str
    _nbt: dict|None
    
    def __init__(self, value: str, data: dict | None = None) -> None:
        """NEEDS REFACTOR

        Args:
            value (str): The value for this entity
        """
        self.data = EntityData()
        self._value = value
        self._nbt = data
    
    @t.overload
    def selector(cls, selector: Selector) -> 'Entity':
        ...
    
    @t.overload
    def selector(cls, selector: Selector, data: dict | None = None) -> 'Entity':
        ...
    
    @classmethod
    def selector(cls, selector: Selector, data: dict | None = None) -> 'Entity':
        """Generates an entity from a selector, can be overloaded with NBT data

        Args:
            selector (Selector): What entity(s) to select
            data (dict, optional): NBT Data to add to the entity. Defaults to None.

        Returns:
            Entity: This instance
        """
        instance = cls(selector, data)
        return instance
    
    def nbt(self, data: dict[str, t.Any]) -> t.Self:
        self._nbt = data
        return self
    
    @property
    def cmd_str(self) -> str:
        if not self._nbt:
            return f"{self._value}"
        return f"{self._value}[{self._nbt}]"