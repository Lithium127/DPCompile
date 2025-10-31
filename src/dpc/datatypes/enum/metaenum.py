

class EnumMeta(type):
    def __delattr__(cls, name):
        raise AttributeError(f"Cannot delete attribute '{name}' from enum {cls.__name__}")
    
    def __setattr__(cls, name, val):
        raise AttributeError(f"Cannot modify attribute '{name}' from enum {cls.__name__}. Attempted value '{val}'")
    
    def __getattribute__(cls, name):
        data = super().__getattribute__(name)
        if isinstance(data, dict):
            instance = cls._type_as(**data)
            return instance
        return data