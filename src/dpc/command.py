"""
The module that holds all command classes, enabling minimal code and
checking errors at build time.
"""
from __future__ import annotations
import typing as t

from abc import ABC, abstractmethod

from .datatypes import Version, TextElement
from .datatypes import to_textelement

if t.TYPE_CHECKING:
    from .IO.script import ScriptContext, Script

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

class Command(BaseCommand):
    """A literal command without structure, appending
    its content directly to a script."""
    
    content: str
    
    def __init__(self, content: str, **kwargs):
        """A literal command without structure, returns
        the base string passed to the command when built.
        
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
        self.content = content
    
    def build(self):
        if "\n" in self.content:
            return "\n".join([f"# {line}" for line in self.content.split("\n")])
        return f"# {self.content}"



class Log(BaseCommand):
    """Shorthand say command with script detection and warning levels for development.
    automatically flagged as developmet to avoid."""
    
    _COLOR_MAPPING = {
        'info' : TextElement.Colors.WHITE,
        'warning' : TextElement.Colors.YELLOW,
        'critical' : TextElement.Colors.RED
    }
    
    _script: Script | None
    msg: str
    level: str
    
    def __init__(self, msg: str, level: t.Literal["info", "warning", "critical"] = "info", **kwargs):
        """Creates a development only log message. Shorthand for the Say command
        but identifies the script is is created within and automatically marks
        itself as development only, making it safe to run within the script environment
        as it gets masked out when the production environ is run.

        Args:
            msg (str): The message to log, this message will be displayed to the text chat when
                        its parent script is run, and the message will include the log level and
                        the name of the script that parents it if a script could be found.
            level (Literal[info, warning, critical], optional): The level for this log instance.
                        Can be info, warning, or critical. Note that these logs are hard-coded
                        within the pack and cannot be conditionally run without use of an execute
                        command. Defaults to "info".
        """
        super().__init__(dev = True, **kwargs)
        
        self.msg = msg
        self.level = level
        self._script = None
        if BaseCommand._CURRENT_CONTEXT is not None:
            self._script = BaseCommand._CURRENT_CONTEXT.script
    
    @classmethod
    def info(cls, msg: str, **kwargs) -> Log:
        """Creates a log command with the level of info"""
        instance = cls.__new__(cls)
        instance.__init__(msg, level='info', **kwargs)
        return instance

    @classmethod
    def warn(cls, msg: str, **kwargs) -> Log:
        """Creates a log command with the level of info"""
        instance = cls.__new__(cls)
        instance.__init__(msg, level='warning', **kwargs)
        return instance
    
    @classmethod
    def crit(cls, msg: str, **kwargs) -> Log:
        instance = cls.__new__(cls)
        instance.__init__(msg, level='critical', **kwargs)
        return instance
    
    def build(self):
        # TODO: Replace selector with entity selector enum
        instance = TextElement(
            f"[{self._script.name or 'N/A'} | {self.level}] - {self.msg}", 
            color = Log._COLOR_MAPPING.get(self.level, TextElement.Colors.WHITE)
        )
        return f"tellraw @a {instance.to_command_str()}"


class CallFunction(BaseCommand):
    """Command that calls another function as a namespace and path"""
    
    target_name: str
    
    def __init__(self, target_name: str, **kwargs):
        """Creates a call to a function with the given
        name. Names must consist of a namespace and a
        path to the function that includes the name of
        the function.
        
        example: `namespace:path/to/function` or 
        `tcev:raycasts/run_at_block`

        Args:
            target_name (str): _description_
        """
        super().__init__(**kwargs)
        self.target_name = target_name
    
    def build(self):
        return f"function {self.target_name}"

class WrapComment(BaseCommandContext):
    
    content: tuple[str, str]
    
    def __init__(self, start: str, end: str):
        self.content = (start, end)
        
    def __enter__(self):
        Comment(self.content[0])
        return self
    
    def __exit__(self, exc_type, exc, tb):
        Comment(self.content[1])
        return True