from __future__ import annotations
import typing as t

from abc import ABC, abstractmethod

from ..datatypes.version import Version

if t.TYPE_CHECKING:
    from ..IO.script import ScriptContext, Script
    from ..packdsl import PackDSL


def get_current_pack() -> PackDSL:
    if BaseCommand._CURRENT_CONTEXT is None:
        raise ValueError("get_current_pack() called without PackDSL context being attached")
    return BaseCommand._CURRENT_CONTEXT.script.pack


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
    masked: bool
    """Wether or not this command should be omitted from the final 
    build. Used when passing commands as arguments into other 
    commands"""
    
    def __init__(self, register: bool = True, dev: bool = False) -> None:
        """Initializes a command, registering it to a context
        if one is available and the register flag is true.

        Args:
            register (bool, optional): If this command should be registered. Defaults to True.
            dev (bool, optional): If this command is development only. Development only commands
                                  are omitted from the render when building in production mode. 
                                  Defaults to False.
        """
        # All commands are not dev-only unless otherwise stated
        self.is_dev = dev
        # All commands are default marked non-masked
        self.is_masked = False
        
        if BaseCommand._CURRENT_CONTEXT is not None and register:
            if BaseCommand._CURRENT_CONTEXT.script.pack._build_dev or (not self.is_dev):
                print(f"{BaseCommand._CURRENT_CONTEXT.script.name} Building {type(self)}")
                BaseCommand._CURRENT_CONTEXT.add_cmd(self)
    
    def __init_subclass__(cls, min_version: Version | None = None, max_version: Version | None = None):
        cls._VERSION_RANGE = (min_version or Version.min(), max_version or Version.max())
        return super().__init_subclass__()
    
    def __str__(self) -> str:
        # Mask commands that have been converted to strings to avoid repeats. 
        # This will not work for commands passed as other arguments
        self.mask()
        return self.build()

    def _build_for_script(self) -> str | None:
        """Builds a command for insertion into a script.
        If this returns `None` the command is ommitted
        from the final render. This command is not intended
        to be run outside of the action of script building
        and the `BaseCommand.build()` function should be
        prefered to obtain command content.

        Returns:
            str | None: The result of the built command or None.
        """
        if self.is_masked:
            return None
        return self.build()

    @abstractmethod
    def build(self) -> str:
        """build the content of this command as a single
        string without line breaks. The usage dictates that
        the string returned by this be interpretable by the
        .mcfunction filetype.

        If this method is being run manually on a floating
        instance, it is recommended to use the `str()` type
        or to run the commands `__str__()` method to mark the
        command as masked automatically and omit its content
        from the final render.
        
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
    
    def mask(self) -> BaseCommand:
        """Permenantly marks this command as `masked`. 
        Omitting it from the final render. Running this
        method multiple times does not have any effect

        Returns:
            BaseCommand: The instance that was masked.
        """
        self.is_masked = True
        return self
    
    def dev(self, value=True) -> BaseCommand:
        """Makes a command's `is_dev` flag equal to the value
        of the argument.

        Args:
            value (bool, optional): If this command is dev or not. Defaults to True.

        Returns:
            BaseCommand: The instance being set
        """
        self.is_dev = value
        return self
    
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
    """A command that operates within a context"""
    
    @abstractmethod
    def __enter__(self) -> BaseCommandContext:
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc, tb) -> bool:
        pass

class Command(BaseCommand):
    """A literal command without structure, appending
    its content directly to a script."""
    
    content: str
    
    def __init__(self, content: str, **kwargs):
        """A literal command without structure, returns
        the base string passed to the command when built.

        This class exists for implementing custom commands
        or literals that should be appended to the resulting
        file without the need for excessive classes.
        
        ```python
        cmd = Command("This is a test command")
        cmd.build() # > str('This is a test command')
        ```

        Args:
            content (str): The content of the command
        """
        super().__init__(**kwargs)
        self.content = content
    
    def build(self):
        return self.content

class Comment(BaseCommand):
    """A comment within a script, for developer notes"""
    
    content: str
    
    def __init__(self, content: str, **kwargs):
        super().__init__(**kwargs)
        self.content = str(content)
    
    def build(self):
        if "\n" in self.content:
            return "\n".join([f"# {line}" for line in self.content.split("\n")])
        return f"# {self.content}"
