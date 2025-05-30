from __future__ import annotations
import typing as t

from abc import ABC, abstractmethod

from ..datatypes import Version

if t.TYPE_CHECKING:
    from ..IO.script import ScriptContext, Script


class CommandError(Exception):
    """Represents an error occurring within a command"""
    pass


class BaseCommand(ABC):
    """The base class for all commands.
    
    All commands must override the `build()`
    method to return the rendered content of
    the command in a way that can be interpreted
    by the `.mcfunction` filetype, this method
    is called by a script within the `render()`
    method which is used to directly attach the
    content from the command to a script context
    for writing."""
    
    _CURRENT_CONTEXT: ScriptContext | None = None
    
    _VERSION_RANGE: tuple[Version, Version]
    
    is_dev: bool
    
    def __init__(self, register: bool = True, dev: bool = False) -> None:
        """Initializes a command, registering it to a context
        if one is available and the register flag is true

        Args:
            register (bool, optional): If this command should be registered. Defaults to True.
        """
        # All commands are not dev-only unless otherwise stated
        self.is_dev = dev
        
        if BaseCommand._CURRENT_CONTEXT is not None and register:
            if BaseCommand._CURRENT_CONTEXT.script.pack._build_dev or (not self.is_dev):
                BaseCommand._CURRENT_CONTEXT.add_cmd(self)
    
    def __init_subclass__(cls, min_version: Version | None = None, max_version: Version | None = None):
        cls._VERSION_RANGE = (min_version or Version.min(), max_version or Version.max())
        return super().__init_subclass__()
    
    @abstractmethod
    def build(self) -> str:
        """build the content of this command as a single
        string without line breaks. The usage dictates that
        the string returned by this be interpretable by the
        .mcfunction filetype.
        
        > This function can be run multiple times, meaning it should
        not directly modify any attributes of classes in an additive
        manner, preferably at all.

        Returns:
            str: The string this instance represents
        """
        pass
    
    @classmethod
    def validate(cls: BaseCommand, cmdstr: str) -> bool:
        """An optionally overriden method that determines if
        a given string command is a valid string for this
        command instance. Usually checks each value of the
        command string or literal to validate.

        Args:
            cmdstr (str): The literal string to validate

        Returns:
            bool: If the passed literal matches required 
                    argument positions for this command
        """
        return True
    
    @classmethod
    def _set_context(cls, ctx: ScriptContext) -> None:
        """Sets the reference to the current available 
        script context for all commands.
        
        This context must be writable, as all commands
        that are rendered while the context is set have
        their content directly appended to the script
        context.

        Args:
            ctx (ScriptContext): The script context
        """
        BaseCommand._CURRENT_CONTEXT = ctx
    
    @classmethod
    def _pop_context(cls) -> None:
        """Removes the reference to the script context"""
        BaseCommand._CURRENT_CONTEXT = None

class BaseCommandContext(ABC):
    
    @abstractmethod
    def __enter__(self) -> BaseCommandContext:
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc, tb) -> bool:
        pass