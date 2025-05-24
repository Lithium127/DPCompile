from __future__ import annotations
import typing as t
from enum import Enum

from .selector import Selector, ensure_selector

from ..command import Command, BaseCommand

if t.TYPE_CHECKING:
    from ..packdsl import PackDSL

# TODO: Move to command.py
def get_current_pack() -> PackDSL:
    if BaseCommand._CURRENT_CONTEXT is None:
        raise ValueError("Pack not set")
    return BaseCommand._CURRENT_CONTEXT.script.pack



class ScoreCriteria(Enum):
    """Enumeration of all valid scoreboard criteria"""
    
    DUMMY = "dummy"
    """This scoreboard will not increase in value through natural means, requiring the scoreboard command to explicitly set its value."""


class ScoreboardClosure(BaseCommand):
    """Represents a scoreboard command targeting a set
    amount of data."""
    
    _content: str
    
    def __init__(self, content: str, **kwargs):
        super().__init__(**kwargs)
        self._content = content
    
    def build(self):
        return f"scoreboard {self._content}"


class Scoreboard:
    """Represents a scoreboard that can store a value per entity within the game.
    
    Scoreboard are automatically managed by the pack that parents commands that
    modify the attributes of the board."""
    
    _SCOREBOARD_REGISTRY: dict[str, Scoreboard] = {}
    
    _name: str
    _criteria: str
    _registered_in: set[PackDSL]
    
    def __new__(cls, name: str, *args, **kwargs) -> Scoreboard:
        if name in cls._SCOREBOARD_REGISTRY:
            return cls._SCOREBOARD_REGISTRY[name]
        instance = super().__new__(cls)
        cls._SCOREBOARD_REGISTRY[name] = instance
        return instance
    
    def __init__(self, name: str, *, criteria: str = None):
        """Instances a new scoreboard with the given name.
        If the board already exists then it returns the
        pre-existing instance with that name, meaning instances
        can be referenced between modules without needing to
        directly pass the instance if the name is known.
        
        The name of the scoreboard is relative to the pack that
        it is parented by, organized with the namespace of the
        pack preceeding the name of the scoreboard, see the
        `name()` method for a more detailed explaination of how
        naming works.

        Args:
            name (str): The name of this scoreboard.
        """
        self._name = name
        self._criteria = criteria or ScoreCriteria.DUMMY.value
        self._registered_in = set()
        
    @classmethod
    def initialize_scoreboards(self) -> None:
        """Sets all scoreboards that are attached to a given
        pack found from the current script context and creates
        all scoreboards attached.
        """
        pack = get_current_pack()
        if len(pack._scoreboards) < 1:
            Command("# No scoreboards to initialize")
            return
        for scoreboard in pack._scoreboards:
            scoreboard.create()
    
    
    def set_criteria(self, criteria: str) -> None:
        self._criteria = criteria
        
    
    @property
    def real_name(self) -> str:
        return self._name
    
    def name(self) -> str:
        """Builds the pack-relative name of this scoreboard.
        Each scoreboard is relative to the namespace of the
        pack it is instanced within to avoid naming
        conflicts. Names are seperated with an underscore
        between the scoreboard name and the pack namespace
        
        `<namespace>_<scoreboard>`
        
        `test_score` -> Scoreboard with name `score` instanced in pack
        with namespace `test`.
        
        If no pack is found, or `None` is passed for the argument
        with pack, this method returns the pure name of this
        scoreboard, as it is referenced within the scoreboard
        registry.

        Args:
            pack (PackDSL): The pack to build with

        Returns:
            str: The name of the scoreboard
        """
        return (f"{get_current_pack()._namespace}_" or "") + self.real_name
    
    def set_value(self, target: Selector | str, value: int, **kwargs) -> ScoreboardClosure:
        """Generates a command, and if a script context
        is set, attaches that command to the build context,
        that sets the value of a given scoreboard for all
        targets of a given selector.
        
        This function will attach the scoreboard to a list
        that is created is a `load` file at runtime

        Args:
            target (Selector | str): The given selector that defines what this command should target
            value (int): The integer value to set the targets score to.
        """
        self._add_to_pack_registry()
        return ScoreboardClosure(f"players set {ensure_selector(target).to_command_str()} {self.name()} {value}", **kwargs)
    
    
    def increment(self, target: Selector | str, value: int, **kwargs) -> ScoreboardClosure:
        self._add_to_pack_registry()
        return ScoreboardClosure(f"players add {ensure_selector(target).to_command_str()} {self.name()} {value}", **kwargs)
    
    
    def create(self) -> BaseCommand:
        """Generates a command that initializes
        this scoreboard within the game. Automatically
        created if this scoreboard is attached to a pack.

        Returns:
            BaseCommand: The command instance
        """
        self._add_to_pack_registry()
        return Command(f"scoreboard objectives add {self.name()} {self._criteria}")
    
    
    def reset(self, target: Selector | str, **kwargs) -> BaseCommand:
        self._add_to_pack_registry()
        return Command(f"scoreboard players set {ensure_selector(target).to_command_str()} {self.name()} 0")
    
    
    def _add_to_pack_registry(self) -> PackDSL:
        """An internal command that adds this
        scoreboard to a packs registry. This
        method is called whenever a command is
        generated by this instance.
        
        This command informs that pack that this
        scoreboard instance is pertinent to the
        current pack, and should be created by
        an automatically generated loading script.
        
        This method also sets the value of `_current_pack` 
        for this instance to make obtaining the scoreboard 
        name easier.
        """
        pack = get_current_pack()
        if pack._namespace not in self._registered_in:
            pack.register_scoreboard(self)
            self._registered_in.add(pack._namespace)