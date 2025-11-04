import typing as t

T = t.TypeVar("T")
class EnumMeta(type, t.Generic[T]):
    """Shared Enum Metatype. Classes that use this
    will have their attributes interpreted as arguments
    and will instance new objects when their attributes
    are queried. Classes will also become iterable.
    
    Example Usage:
    ```python
    class Items(metatype = EnumMeta[Item]):
        IRON_SWORD = {"id":0, ...}
    ```"""
    _generic_type: t.Type[T] | None = None  # store T at runtime

    def __class_getitem__(cls, item_type: t.Type[T]):
        # Create a subclass of this metaclass that remembers the type
        namespace = dict(cls.__dict__)
        namespace["_generic_type"] = item_type
        return type(cls.__name__, (cls,), namespace)
    
    def __delattr__(cls, name):
        raise AttributeError(f"Cannot delete attribute '{name}' from enum {cls.__name__}")
    
    def __setattr__(cls, name, val):
        raise AttributeError(f"Cannot modify attribute '{name}' from enum {cls.__name__}. Attempted value '{val}'")
    
    def __getattribute__(cls, name: str):
        data = super().__getattribute__(name)
        if not name.startswith("_"):
            if isinstance(data, dict):
                return cls._generic_type(**data)
        return data

    def __iter__(cls) -> t.Iterator[T]:
        for name in cls.__dict__:
            if not name.startswith("_"):
                yield getattr(cls, name)
    
    def filter(cls, filter: t.Callable | t.Any) -> t.Iterator[T]:
        """Iterates through members of this class
        yielding members that equal the filter.

        Filter can be a callable or a value.
        """

        if not callable(filter):
            filter_val = filter
            filter = lambda x: (x == filter_val)
        
        for val in cls:
            if filter(val):
                yield val