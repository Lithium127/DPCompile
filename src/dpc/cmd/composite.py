"""
A collection of shorthand commands or custom commands that wrap multiple
different command instances together. Requires that Command 
"""
from __future__ import annotations
import typing as t


from .bases import BaseCommand
from . import command as cmd

from ..datatypes.textelement import TextElement

if t.TYPE_CHECKING:
    from ..IO.script import Script


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
    
    def render(self):
        # TODO: Replace selector with entity selector enum
        script_name = (self._script.name or 'N/A')
        if (self._script._parent != self._script.pack):
            script_name = (f"{self._script._parent.__class__.__name__}.{script_name}")
        
        instance = TextElement(
            f"[{script_name} | {self.level}] - {self.msg}", 
            color = Log._COLOR_MAPPING.get(self.level, TextElement.Colors.WHITE)
        )
        return cmd.TellRaw("a", instance).mask().build()


class ExecuteRandom(BaseCommand):
    """Selects a random command from given options"""

    options: list[BaseCommand]

    def __init__(self, *options: BaseCommand, **kwargs):
        super().__init__(**kwargs)
        self.options = list(*options)
    
    def render(self):
        return cmd.TellRaw("a", "test")