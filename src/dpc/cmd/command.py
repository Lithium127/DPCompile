"""
The module that holds all command classes, enabling minimal code and
checking errors at build time.
"""
from __future__ import annotations
import typing as t

from ..datatypes import TextElement

if t.TYPE_CHECKING:
    from ..IO.script import Script


from .bases import BaseCommand, BaseCommandContext




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
        'info' : "white",
        'warning' : "yellow",
        'critical' : "red"
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