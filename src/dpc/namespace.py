from __future__ import annotations
import typing as t

# Maybe deffered namespace resolution support


class Namespace:
    """Represents a named singleton space for objects within a pack to 
    be registered to. Objects that share a namespace cannot have 
    duplicate entries.
    
    Two instanced spaces with the same name will reference the same objet"""

    _REGISTERED_SPACES: dict[str, Namespace] = dict()

    _identifier: str
    _local_registry: list[t.Any]

    def __new__(cls, id: str, *args, **kwargs):
        if id in cls._REGISTERED_SPACES.keys():
            return cls._REGISTERED_SPACES[id]
        
        # Otherwise make a new namespacespace
        instance = super().__new__(cls)
        instance._identifier = id
        cls._REGISTERED_SPACES[id] = instance
        return instance

    def __init__(self, id: str, /):
        self._identifier = id
        self._local_registry = list()
    
    def __str__(self):
        return self._identifier
    
    def __hash__(self):
        return object.__hash__(self)
    
    def __eq__(self, value: object, /):
        if not isinstance(value, Namespace):
            return False
        
        return self._identifier == value._identifier

    @property
    def identifier(self) -> str:
        return self._identifier