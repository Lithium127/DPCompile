from __future__ import annotations
import typing as t
from enum import Enum

from .selector import ensure_selector

from ..cmd.command import Command, BaseCommand

if t.TYPE_CHECKING:
    from ..packdsl import PackDSL
    from .selector import Selector

# TODO: Move to command.py
def get_current_pack() -> PackDSL:
    if BaseCommand._CURRENT_CONTEXT is None:
        raise ValueError("Pack not set")
    return BaseCommand._CURRENT_CONTEXT.script.pack


class ScoreCriteria:
    """Enumeration of all valid scoreboard criteria. Descriptions are added for each
    available option from the minecraft wiki"""
    
    @staticmethod
    def dummy() -> str:
        """This scoreboard will not increase in value through natural means, requiring the scoreboard command to explicitly set its value."""
        return "dummy"
    
    @staticmethod
    def trigger() -> str:
        """Score is only changed by commands, and not by game events such as death. The `/trigger` command can be used by a 
        player to set or increment/decrement their own score in an objective with this criterion. The `/trigger` command 
        fails if the objective has not been "enabled" for the player using it, and the objective is disabled for the player 
        after using the `/trigger` command on it. Note that the `/trigger` command can be used by ordinary players even if Cheats 
        are off and they are not an Operator. This is useful for player input via `/tellraw` interfaces."""
        return "trigger"
    
    @staticmethod
    def death_count() -> str:
        """Score increments automatically for a player when they die."""
        return "deathCount"
    
    @staticmethod
    def player_kill_count() -> str:
        """Score increments automatically for a player when they kill another player."""
        return "playerKillCount"
    
    @staticmethod
    def total_kill_count() -> str:
        """Score increments automatically for a player when they kill another player or a mob."""
        return "totalKillCount"
    
    @staticmethod
    def health() -> str:
        """Ranges from 0 to 20 on a normal player; represents the amount of half-hearts the player has. May appear as 0 for players 
        before their health has changed for the first time. Extra hearts and absorption hearts also count to the health score, 
        meaning that with Attributes/Modifiers or the Health Boost or Absorption status effects, health can far surpass 20."""
        return "health"
    
    @staticmethod
    def experience() -> str:
        """Matches the total amount of experience the player has collected since their last death (or in other words, their score)."""
        return "xp"

    @staticmethod
    def level() -> str:
        """Matches the current experience level of the player."""
        return "level"
    
    @staticmethod
    def food() -> str:
        """Ranges from 0 to 20; represents the amount of hunger points the player has. May appear as 0 for players before their foodLevel has changed for the first time."""
        return "food"
    
    @staticmethod
    def air() -> str:
        """Ranges from 0 to 300; represents the amount of air the player has left from swimming under water, matches the air nbt tag of the player."""
        return "air"
    
    @staticmethod
    def armor() -> str:
        """Ranges from 0 to 20; represents the amount of armor points the player has. May appear as 0 for players before their armor has changed for the first time."""
        return "armor"
    
    @staticmethod
    def team_kill(team: t.Literal["black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple", "gold", "gray", "dark_gray", "blue", "green", "aqua", "red", "light_purple", "yellow", "white"]) -> str:
        """Sub-criteria include team colors. Player scores increment when a player kills a member of the given colored team."""
        return f"teamkill.{team}"
    
    @staticmethod
    def killed_by_team(team: t.Literal["black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple", "gold", "gray", "dark_gray", "blue", "green", "aqua", "red", "light_purple", "yellow", "white"]) -> str:
        """Sub-criteria include team colors. Player scores increment when a player has been killed by a member of the given colored team."""
        return f"killedByTeam.{team}"


MODIFIABLE_CRITERIA = [
    ScoreCriteria.dummy(),
    ScoreCriteria.trigger(),
    ScoreCriteria.death_count(),
    ScoreCriteria.player_kill_count(),
    ScoreCriteria.total_kill_count()
]

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
        if getattr(self, "_criteria", None) is None:
            self._criteria = criteria or ScoreCriteria.dummy()
        elif criteria is not None:
            raise RuntimeError(f"Conflicting criteria given for scoreboard {self.name()} init call, " + 
                               f"already of criteria <{self._criteria}> and passed <{criteria}>. To " + 
                               "set criteria for existing scoreboard use ScoreBoard.set_criteria(str)")
        if getattr(self, "_registered_in", None) is None:
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
    def modify_allowed(self) -> bool:
        return (self._criteria in MODIFIABLE_CRITERIA)
        
    
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
    
    
    def _modify(self, operation: t.Literal["set", "add"], target: Selector | str, value: int, **kwargs) -> ScoreboardClosure:
        """Generates and attaches a command that modifies a scoreboard by or to a set value
        for a given target. Unused kwargs are passed to the command init method.

        Args:
            operation (t.Literal[&quot;set&quot;, &quot;add&quot;]): The operation to be performed
            target (Selector | str): The selector providing targets for modification
            value (int): The value to modify by

        Raises:
            RuntimeError: If the scoreboards current criteria does not permit modification

        Returns:
            ScoreboardClosure: The command instance
        """
        self._add_to_pack_registry()
        if not self.modify_allowed:
            raise RuntimeError(f"Modification of scoreboard with criteria <{self._criteria}> not permitted during pack execution. Build aborted")
        return ScoreboardClosure(f"players {operation} {ensure_selector(target).to_command_str()} {self.name()} {value}", **kwargs)
    
    
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
        return self._modify("set", target, value, **kwargs)
    
    
    def increment(self, target: Selector | str, value: int, **kwargs) -> ScoreboardClosure:
        return self._modify("add", target, value, **kwargs)
    
    
    def decrement(self, target: Selector | str, value: int, **kwargs) -> ScoreboardClosure:
        return self._modify("add", target, value, **kwargs)
    
    
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
        self.set_value(target, 0, **kwargs)
    
    
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