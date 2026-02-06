"""
The module that holds all command classes, enabling minimal code and
checking errors at build time.
"""
from __future__ import annotations
import typing as t

from .bases import BaseCommand, CommandError, cmdargs, cmdstr

from ..datatypes.version import require_version

from ..datatypes.position import Position, positionlike
from ..datatypes.entity import ensure_selector, SelectorEnum, Selector
from ..datatypes.textelement import TextElement
from ..datatypes.block import Block, BlockState

if t.TYPE_CHECKING:
    from ..datatypes.entity import SelectorLiteral, PlayerSelectorLiteral



class CallFunction(BaseCommand):
    """Command that calls another function using a namespace and path"""
    
    target_name: str
    
    def __init__(self, script: t.Any, **kwargs):
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
        self.target_name = script
    
    def render(self):
        return "function", self.target_name
    
    @classmethod
    def validate(cls, cmdstr):
        if len(cmdargs(cmdstr)) != 2:
            return False
        return True


class Clear(BaseCommand):

    target: Selector | str
    item: str | None
    max_count: int | None

    def __init__(self, target: Selector | PlayerSelectorLiteral, item: str = None, max_count: int = None, **kwargs):
        super().__init__(**kwargs)
        self.target = ensure_selector(target)
        self.item = item
        self.max_count = max_count
    
    def render(self):
        return "clear", self.target, self.item, self.max_count
    
    @classmethod
    def validate(cls, cmdstr):
        args: tuple[str] = cmdargs(cmdstr)
        if len(args) < 2 or len(args) > 4:
            return False
        
        if len(args) == 4:
            if not args[3].isdigit():
                return False

        return True


class Clone(BaseCommand):
    """Clones blocks from one region to another"""

    bounds: tuple[Position, Position]
    destination: Position
    block_mask: str | BlockState | None
    mode: str
    source_dim: str | None
    dest_dim: str | None

    def __init__(self, begin: positionlike, end: positionlike, destination: positionlike, mask: t.Literal["replace", "masked"] | BlockState = None, mode: t.Literal["force", "move", "normal"] = None, *, source_dim: str = None, dest_dim: str = None, **kwargs):
        """Clones Blocks from one region to another.
        
        Block position is the coordinates of the point at the lower northwest corner of a block. 
        Because of this, the lesser coordinates of each axis falls right on the region boundary, 
        but the greater coordinates are one block from the boundary, and the block volume of the 
        source region is `(xgreater - xlesser + 1) x (ygreater - ylesser + 1) x 
        (zgreater - zlesser + 1)`. For example, `0 0 0 0 0 0` has a 1-block volume, and 
        `0 0 0 1 1 1` and `1 1 1 0 0 0` both identify the same region with an 8-block volume.
        
        Args:
            begin (positionlike): Specifies the first coordinates of two opposing corner blocks of the source region.
            end (positionlike): Specifies the second coordinates of two opposing corner blocks of the source region.
            destination (positionlike): Specifies the lower northwest (negative `x` and `z`) corner of the destination region.
            mask (["replace", "masked"] | BlockState, optional): Specifies whether to filter the blocks being cloned. 
                        If set to `replace`, this command will copy all blocks, overwriting all blocks of the destination 
                        region with the blocks from the source region. If set to `masked`, this command will copy only 
                        non-air blocks. Blocks in the destination region that would otherwise be overwritten by air are 
                        left unmodified. If set to a `BlockState` only blocks of the specified filter will be copied. 
                        
                        If left unspecified defaults to `replace`. Defaults to None.
            mode (["force", "move", "normal"], optional): Specifies how to treat the source region. If set to `force` this 
                        command will force the clone even if the source and destination regions overlap. If set to `move` 
                        this command will Clone the source region to the destination region, then replace the source region 
                        with air. When used in filtered mask mode, only the cloned blocks are replaced with air. If set to 
                        `normal` this command will not move or force. 
                        
                        If left unspecified, defaults to `normal`. Defaults to None.
            source_dim (str, optional): Specifies the dimension to clone the blocks from. If unspecified, defaults to current execution dimension.. Defaults to None.
            dest_dim (str, optional): Specifies the dimension to clone the blocks to. If unspecified, defaults to current execution dimension.. Defaults to None.
        """
        super().__init__(**kwargs)
        self.bounds = (Position(begin), Position(end))
        self.destination = Position(destination)
        self.block_mask = mask
        if isinstance(self.block_mask, Block):
            self.block_mask = self.block_mask()

        self.source_dim = source_dim
        self.dest_dim = dest_dim

        self.mode = mode or "normal"
    
    def render(self):
        source_dim_str = f"from {self.source_dim}" if self.source_dim is not None else None
        dest_dim_str = f"to {self.dest_dim}" if self.dest_dim is not None else None
        block_mask = f"filtered {self.block_mask}" if isinstance(self.block_mask, BlockState) else self.block_mask

        return "clone", source_dim_str, self.begin, self.end, dest_dim_str, self.destination, block_mask, self.mode if self.block_mask is not None else None
    

    def contains(self, value: Position) -> bool:
        """Returns true if the given position is contained within the 
        bounding box of this commands source positions. Note that this
        will not be functionally useful in a datapack runtime environment
        however pre-set positions can be checked at compile time for
        errors and similar known mistakes.

        Args:
            value (Position): The position to query

        Returns:
            bool: True if this position is contained by this command
        """
        return (
            (value.x <= min(self.begin.x, self.end.x) or value.x > max(self.begin.x, self.end.x)) and 
            (value.y <= min(self.begin.y, self.end.y) or value.y > max(self.begin.y, self.end.y)) and 
            (value.z <= min(self.begin.z, self.end.z) or value.z > max(self.begin.z, self.end.z))
            )


    @property
    def volume(self) -> int:
        """The internal volume of the cloned region"""
        return (max(self.begin.x, self.end.x) - min(self.begin.x, self.end.x) + 1
           ) * (max(self.begin.y, self.end.y) - min(self.begin.y, self.end.y) + 1
           ) * (max(self.begin.z, self.end.z) - min(self.begin.z, self.end.z) + 1)
    

    @property
    def begin(self) -> Position:
        """The first position defined where blocks will be cloned from"""
        return self.bounds[0]
    
    @property
    def end(self) -> Position:
        """The second position defined where blocks will be cloned from"""
        return self.bounds[1]


class Execute(BaseCommand):

    class _Argument:
        """Data holding class describing a single argument
        in a compound command. Does nothing with the data
        until rendering happens.
        """

        values: list[t.Any]

        def __init__(self, *args):
            self.values = [value for value in args]
        
        def render(self) -> str:
            return cmdstr(*self.values)

    arguments: list[_Argument]
    cmd: BaseCommand | None

    def __init__(self, cmd: BaseCommand | None = None, **kwargs):
        """Executes another command but allows changing the executor, 
        changing the position and angle it is executed at, adding 
        preconditions, and storing its result.

        Args:
            cmd (BaseCommand, optional): The command this instance will execute. s. Defaults to None.
        """
        super().__init__(**kwargs)
        self.cmd = cmd
        self.arguments = []
    
    def render(self):
        return "execute", *[arg.render() for arg in self.arguments], (f"run {self.cmd}") if self.cmd is not None else None
    
    def _add_argument(self, *args) -> Execute:
        self.arguments.append(self._Argument(*args))
        return self
    
    def Align(self, axis: t.Literal["x", "y", "z", "xy", "xz", "yz", "xyz"]) -> Execute:
        """Updates the execution position, aligning to its current block position (integer coordinates). 
        Applies only along specified axes. This is akin to rounding the coordinates (i.e., rounding it up 
        if the decimal part is greater than or equal to 0.5, or down if less than 0.5)

        Args:
            axis (['x', 'y', 'z', 'xy', 'xz', 'yz', 'xyz']): The selection of axis to align to. Any non-repeating 
                            combination of the characters 'x', 'y', and 'z' is valid. Axes can be declared in any 
                            order, but they cannot duplicate. (For example, x, xz, zyx, or yz.)

        Returns:
            Execute: The execution instance
        """
        return self._add_argument("align", axis)
    
    def Anchored(self, anchor: t.Literal["eyes", "feet"]) -> Execute:
        """Sets the execution anchor to the eyes or feet. Defaults to feet. Running positioned <pos> -> execute 
        resets to feet. Effectively recenters local coordinates on either the eyes or feet, also changing the 
        angle of the facing subcommand (of `/execute` and `/teleport`) works off of.

        Args:
            anchor (['eyes', 'feet']): The anchor for this object

        Returns:
            Execute: The execution instance
        """
        if not anchor in ["eyes", "feet"]:
            raise CommandError("Invalid anchor passed to execution builder")
        return self._add_argument("anchored", anchor)
    
    def Aas(self, target: SelectorLiteral | Selector) -> Execute:
        """Shorthand for Execute.As(<target>).At(SelectorEnum.S). Sets the executor and the
        position to match the passed selection.

        Args:
            target (SelectorLiteral | Selector): The target selector

        Returns:
            Execute: The execution instance
        """
        return self.As(target).At(SelectorEnum.S)

    def As(self, target: SelectorLiteral | Selector) -> Execute:
        """Sets the executor to target entity, without changing execution position, rotation, dimension, and anchor.

        Args:
            target (SelectorLiteral | Selector): The target selector

        Returns:
            Execute: The execution instance
        """
        return self._add_argument("as", target)

    def At(self, target: SelectorLiteral | Selector) -> Execute:
        """Sets the execution position, rotation, and dimension to match those of an entity; does not change executor.

        Args:
            target (SelectorLiteral | Selector): The target selector

        Returns:
            Execute: The execution instance
        """
        return self._add_argument("at", target)
    
    @t.overload
    def Facing(self, target: Position) -> Execute:
        """Sets the execution rotation to face a given point, as viewed from its anchor (either the eyes or the feet). Forks 
        if <targets> or origin: target selects multiple entities. Terminates current branch if <targets> or origin: target 
        fails to resolve to one or more entities (named players must be online).

        Args:
            target (Position): The position this command will face
        """
    @t.overload
    def Facing(self, target: Selector, anchor: t.Literal["eyes", "feet"] = None) -> Execute:
        """Sets the execution rotation to face a given point, as viewed from its anchor (either the eyes or the feet). Forks 
        if <targets> or origin: target selects multiple entities. Terminates current branch if <targets> or origin: target 
        fails to resolve to one or more entities (named players must be online).

        Args:
            target (Selector): The selector targeting the entity that will be faced
            anchor (['eyes', 'feet'], optional): The anchor that this command will look at on the target entity. Defaults to None.
        """
    
    def Facing(self, target: Position | Selector, anchor: t.Literal["eyes", "feet"] = None) -> Execute:
        if isinstance(target, Selector):
            return self._add_argument("facing", "entity", target, anchor or "feet")
        return self._add_argument("facing", target)

    def In(self, dim: str) -> Execute:
        """Sets the execution dimension and execution position. Respects dimension scaling for relative and local coordinates: 
        the execution position (only the X/Z part) is divided by 8 when changing from the Overworld to the Nether, and is 
        multiplied by 8 when vice versa. Applies to custom dimensions as well.

        Args:
            dim (str): The target dimension to execute in
        """
        return self._add_argument("in", dim)
    
    def On(self, relation: t.Literal["attacker", "controller", "leasher", "origin", "owner", "passengers", "target", "vehicle"]) -> Execute:
        """Executor is updated based on the relation with the executor entity (which changes the meaning of @s). Forks if 
        passengers selects multiple entities. (Other relations can select only at most one entities.) Terminates current 
        branch if the current executor is not an entity. Terminates current branch if the relation is not applicable to 
        the current executor entity or there are no entities matching it.

        A relation to the current executor entity:
            `attacker`: the last entity that damaged the current executor entity in the previous 5 seconds. Note that damage types in minecraft:no_anger tag bypass the record of attacker. Interaction entities do not forget attacker after 5 seconds. Some mobs forget the attacker when ceasing their aggression.
            `controller`: the entity that is riding and controlling the current executor entity. See Riding#Controlling for details.
            `leasher`: the entity leading the current executor entity with a leash.
            `origin`: the entity that cause the summon of the current executor entity. For example, the shooter of an arrow, the primer of a primed TNT entity.
            `owner`: the owner of the current executor entity if it is a tameable animal.
            `passengers`: all entities that are directly riding the current executor entity, no sub-passengers.
            `target`: the target that the current executor entity intends on attacking. Interaction entities can select the last entity that interacted with them.
            `vehicle`: the entity ridden by the current executor entity.

        Args:
            relation (['attacker', 'controller', 'leasher', 'origin', 'owner', 'passengers', 'target', 'vehicle']): The relation to next entity
        """
        require_version("1.19.4")
        return self._add_argument("on", relation)

    def Positioned(self, target: Position | SelectorLiteral | Selector | str) -> Execute:
        """Sets the execution position, without changing execution rotation or dimension; can match an entity's position, or at one block 
        above the Y-level stored in the specified heightmap. Forks if <targets> or origin: target selects multiple entities.
        Terminates current branch if <targets> or origin: target fails to resolve to one or more entities (named players must be online).
        """
        if isinstance(target, str):
            if target.startswith("@") or "[" in target or len(target) < 4:
                target = ensure_selector(target)
            else:
                require_version("1.20")
                return self._add_argument("positioned", "over", target)
        if isinstance(target, Selector):
            return self._add_argument("positioned", "as", target)
        return self._add_argument("positioned", target)


class Kill(BaseCommand):

    target: Selector

    def __init__(self, target: SelectorLiteral | Selector, **kwargs):
        super().__init__(**kwargs)
        self.target = ensure_selector(target)
    
    def render(self):
        return "kill", self.target

class Reload(BaseCommand):
    """Reloads data packs and functions. If a data pack has invalid data 
    (such as an invalid recipe format), changes are not applied and the 
    game continues using the previous data"""

    def __init__(self, **kwargs):
        """Reloads data packs and functions. If a data pack has invalid data 
        (such as an invalid recipe format), changes are not applied and the 
        game continues using the previous data"""
        super().__init__(**kwargs)
        require_version("1.14.4")
    
    def render(self):
        return "reload"


class Return(BaseCommand):
    """A command that can be embedded inside a function to control the execution of the 
    function. Terminate the execution of the function and set the return value of the 
    invoked function to an arbitrary integer value. By setting the return value to an 
    arbitrary value, it can be used to record the execution results of `/function` 
    commands with conditional branches and reflect them in subsequent function executions.
    """

    value: int | BaseCommand

    def __init__(self, value: int | BaseCommand | None, **kwargs):
        """A command that can control the execution of a script or function, returning
        an arbitrary integer value or the result of another command. If a command is 
        passed as the return value that command will be executed and the result will
        be returned by the function at execution.

        If the value passed is `None`, then a failure will be returned by this function.

        Args:
            value (int | BaseCommand | None): The integer or command that will be returned

        Raises:
            CommandError: If the return value is not an integer or a command
        """
        super().__init__(**kwargs)
        require_version("1.20")
        if not (isinstance(value, (int, BaseCommand)) or value is None):
            raise CommandError(f"Return value of type {type(value)} not permitted, requires (int, BaseCommand)")
        
        if  value is None:
            require_version("1.20.3")
        elif isinstance(value, BaseCommand):
            require_version("1.20.2")

        self.value = value
    
    def has_command(self) -> bool:
        """Returns true if this instance of `Return` is returning
        the result of another command.

        Returns:
            bool: If this instance returns a command
        """
        return isinstance(self.value, BaseCommand)
    
    def has_fail(self) -> bool:
        return (self.value is None)

    def render(self):
        if self.has_fail():
            return "return", "fail"
        return "return", "run" if self.has_command() else None, self.value

class TellRaw(BaseCommand):
    """Sends a `TextElement` or `string` message to selected players"""
    
    target: Selector
    content: TextElement

    def __init__(self, target: Selector | PlayerSelectorLiteral, content: TextElement | str, **kwargs):
        """Sends a TextElement message to players

        Args:
            target (Selector | str): _description_
            content (TextElement | str): _description_
        """
        super().__init__(**kwargs)

        self.target = ensure_selector(target)
        if not self.target.targets_player():
            raise CommandError(self, f"Could not initialize {type(self).__name__} instance, Selector '{self.target}' targets entities that are not players.")
        self.content = TextElement(content)

    def render(self):
        return "tellraw", self.target, self.content

