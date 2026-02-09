from __future__ import annotations
import typing as t

from .mctype import MinecraftType

class Literal(MinecraftType):
    """Represents a literal datatype than can be added to a command."""
    
    value: t.Any
    
    def __init__(self, value: t.Any) -> None:
        """Represents a literal value as a
        valid datatype for commands. This is
        the fallback class for unknown values
        when passed to `ensure_mctype()` and
        allows for arbitrary values to be passed
        to commands.
        
        Commands and other datatypes should cast
        to this type automatically, meaning this
        should rarely be directly instanced.

        Args:
            value (Any): The value to wrap
        """
        self.value = value
    
    def to_command_str(self):
        return str(self.value)
