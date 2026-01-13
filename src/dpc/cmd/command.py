"""
The module that holds all command classes, enabling minimal code and
checking errors at build time.
"""
from __future__ import annotations
import typing as t

from .bases import BaseCommand, CommandError, cmdargs

from ..datatypes.version import require_version

from ..datatypes.position import Position, positionlike
from ..datatypes.entity import ensure_selector
from ..datatypes.textelement import TextElement
from ..datatypes.block import Block, BlockState

if t.TYPE_CHECKING:
    from ..datatypes.entity import Selector, SelectorLiteral, PlayerSelectorLiteral



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

        return "clone", source_dim_str, self.begin, self.end, dest_dim_str, self.destination, block_mask, self.mode
    

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
        if isinstance(value, BaseCommand) or value is None:
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

