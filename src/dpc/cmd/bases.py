from __future__ import annotations
import typing as t

from abc import ABC, abstractmethod
from collections.abc import Iterable
import copy

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
    command: BaseCommand

    def __init__(self, cmd: BaseCommand, *args):
        super().__init__(f"Exception occurred in {cmd.__class__.__name__} command. " + ','.join(args))
        self.command = cmd


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
    _is_registered: bool
    
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
        
        self._is_registered = False
        if BaseCommand._CURRENT_CONTEXT is not None and register:
            self._register()
    
    def __init_subclass__(cls, min_version: Version | None = None, max_version: Version | None = None):
        cls._VERSION_RANGE = (min_version or Version.minimum(), max_version or Version.maximum())
        return super().__init_subclass__()
    
    def __str__(self) -> str:
        # Mask commands that have been converted to strings to avoid repeats. 
        # This will not work for commands passed as other arguments
        self.mask()
        return self.build()
    
    def __call__(self, mask: bool = True) -> None | BaseCommand:
        """Calling a command is a method for moving the placement of a given command.
        Especially useful for performing some action with the contents of a command
        while rendering it after some point. 
        
        When called on an unregistered command this action registers this command 
        instance to the current script context. if the operating instance is already 
        registered, this effectively 'moves' the command within a script by creating 
        and registering a deep copy to the pack while masking the previous instance. 
        If a deep copy was made this method returns the new copy.

        Args:
            mask (bool, optional): If this command should be masked in the case it 
                                   has already been added to the script context. 
                                   Defaults to True.
        
        Returns:
            BaseCommand | None: The deep copy of this instance if one was created.
        """
        if not self._is_registered:
            self._register()
        else:
            instance = copy.deepcopy(self)
            instance._register()
            self.mask(mask)
            return instance


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
    
    def _register(self) -> None:
        if BaseCommand._CURRENT_CONTEXT.script.pack._build_dev or (not self.is_dev):
            BaseCommand._CURRENT_CONTEXT.add_cmd(self)
        else:
            BaseCommand._CURRENT_CONTEXT.add_cmd(Comment(f"{self.__class__.__name__} command omitted for production", register=False))
        self._is_registered = True

    def build(self) -> str:
        """Renders and validates a command instance for
        addition to a script. If the command is masked
        this function will still return the rendered
        content for the command, see `_build_for_script()`
        for more information.

        If a command fails validation a `CommandError` is
        raised to avoid building malformed commands, this
        exeption should be handled by the command error
        handler.

        > This function may be run multiple times, meaning it should
        not directly modify any attributes of classes.

        If this method is being run manually on a floating
        instance, it is recommended to use the `str()` type
        or to run the commands `__str__()` method to mark the
        command as masked automatically and omit its content
        from the final render.

        Returns:
            str: The built command string ready for addition to a script.
        """
        value = self.render()
        if not isinstance(value, str) and isinstance(value, Iterable):
            value = cmdstr(*value)
        
        if not self.__class__.validate(value):
            raise CommandError(self, "Malformed command.\nCommand signature failed to match defined pattern, see `validate()` method for more information.")
        
        return value

    @abstractmethod
    def render(self) -> str | list[str] | tuple[str, ...]:
        """build the content of this command as a single
        string without line breaks. The usage dictates that
        the string returned by this be interpretable by the
        .mcfunction filetype. When making a new command see
        the `cmdstr()` function for simple methods of 
        creating the return value.

        This method can return a single string, or an iterable
        of objects that can be converted into strings via the
        `cmdstr()` function.
        
        > This function may be run multiple times, meaning it should
        not directly modify any attributes of classes.

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
    
    def mask(self, value: bool = True, /) -> BaseCommand:
        """Marks this command instance as `masked`, omitting its
        content from the final render. Optionally can *unmask*
        commands which will add their content back into the render
        if done before a given script is written.

        Commands that have been converted to strings (via `str()` or `__str__())
        are automatically masked to avoid repeatedly printing content to
        a given file.

        Args:
            value (bool, optional): If this command should be masked or not. Defaults to True.

        Returns:
            BaseCommand: The command instance that was modified.
        """
        self.is_masked = value
        return self
    
    def dev(self, value=True, /) -> BaseCommand:
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
    def _set_context(cls, ctx: ScriptContext, /) -> None:
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
    
    def __init__(self, *content: str, **kwargs):
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
    
    def render(self):
        return cmdstr(*self.content)

class Comment(BaseCommand):
    """A comment within a script, for developer notes"""
    
    content: str
    
    def __init__(self, content: str, **kwargs):
        super().__init__(**kwargs)
        self.content = str(content)
    
    def render(self):
        # Split line returns into new lines with comments.
        if "\n" in self.content:
            return "\n".join([f"# {line}" for line in self.content.split("\n")])
        return f"# {self.content}"


def _cmd_str_safe(value: t.Any, /) -> str:
    """Evaluates an object to a command safe version. Any object that
    has a `to_command_str()` method will have that method called,
    otherwise the str() value of the object is returned. If the object 
    is `None` then an empty string is returned. This function is safe
    for use in constructing commands.

    Args:
        value (t.Any): The object to evaluate

    Returns:
        str: The command safe string representation of that object.
    """
    if value is None:
        return ""
            
    if hasattr(value, "to_command_str"):
        return value.to_command_str()
    return str(value)


def cmdstr(*args, make_safe: bool = True) -> str:
    """Returns arguments formatted as a command string. Arguments that
    evaluate to `None` have the preceding space omitted and are not
    included in the final render. Takes any number of arguments.

    Args:
        make_safe (bool, optional): If each term should be made command safe. Defaults to True.

    Returns:
        str: The formatted command string
    """

    value = []
    for arg in args:
        if arg is None:
            continue
        if make_safe:
            arg = _cmd_str_safe(arg)
        value.append(arg)
    return " ".join(value)

def cmdargs(cmd: str) -> tuple[str]:
    """Splits a command into an argument list, accounting 
    for strings, json elements, and other non-argument items

    Args:
        cmd (str): The command to convert into arguments

    Returns:
        tuple[str]: The command as arguments
    """
    values = []
    builder = ""

    ctx_pairs: tuple[tuple[str, str]] = (
        ('"', '"'),
        ("{", "}"),
        ("[", "]")
    )
    ctx_index = None

    for item in cmd:
        if ctx_index is None:
            for index, pair in enumerate(ctx_pairs):
                if item == pair[0]:
                    ctx_index = index
                    break
            if ctx_index is None:
                if item == " ":
                    values.append(builder)
                    builder = ""
                else:
                    builder = builder + item
        else:
            if item == ctx_pairs[ctx_index][1]:
                ctx_index = None
    values.append(builder)
    return tuple(values)