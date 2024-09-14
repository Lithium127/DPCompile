
import typing as t

if t.TYPE_CHECKING:
    from .scripts import Script

from .types import (
    NBTData,
    Target,
    ResourceLocation,
    UUID,
    BlockPosition,
    WorldPosition
)


class Command(object):
    """Represents a super-class for all command-like objects"""
    
    line_number: int
    script: 'Script'

    def __init_subclass__(cls) -> None:
        pass
    
    def construct(self) -> str:
        """Builds the command at runtime to allow for relative paths to be decided before reference

        Returns:
            str: The fully constructed command
        """
        return "# Empty Line"
    
    def update_data(self, line_number: int, script: 'Script') -> None:
        """Updates internal data for the command so that it can referece the fine it is contained within

        Args:
            line_number (int): _description_
            filename (str): _description_
        """
        self.script = script
        self.line_number = line_number
    
    def if_exists(self, attr: t.Any) -> str:
        return f" {attr}" if attr else ''
    
    @property
    def name(self) -> str:
        return self.__class__.__name__.lower()


class Advancement(Command):
    """Grants or revokes a selected advancement from target player"""
    
    action: t.Literal["grant", "revoke"]
    target: Target
    condition: t.Literal["everything", "only", "from", "through", "until"]
    advancement: ResourceLocation | None
    criterion: str | None
    
    @t.overload
    def __init__(self, action: t.Literal["grant", "revoke"], target: Target, condition: t.Literal["everything", "only", "from", "through", "until"]) -> None:
        ...
    
    @t.overload
    def __init__(self, action: t.Literal["grant", "revoke"], target: Target, condition: t.Literal["only", "from", "through", "until"], advancement: ResourceLocation) -> None:
        ...
    
    @t.overload
    def __init__(self, action: t.Literal["grant", "revoke"], target: Target, condition: t.Literal["only"], advancement: ResourceLocation, criterion: str | None) -> None:
        ...
    
    def __init__(self, action, target, condition, advancement = None, criterion = None) -> None:
        """Grants or revokes an selected advancement from target player

        Args:
            action ("grant", "revoke"): Weather to grant or revoke the target advancement
            target (Target): The target of the command
            condition (Literal): Where the command should stop
            advancement (ResourceLocation, optional): The location of the advancement. Used for some conditions.
            criterion (str, optional): What criteria the command is looking for, check the wiki for more details. Used for some conditions.
        """
        self.action = action
        self.target = target
        self.condition = condition
        self.advancement = advancement
        self.criterion = criterion

    def construct(self) -> str:
        return f"{self.name} {self.action} {self.target} {self.condition}{' ' + self.advancement if self.advancement else ''}{' ' + self.criterion if self.criterion else ''}"

class Attribute(Command):
    """Gets or modifies an attribute of target entity"""
    
    target: Target
    attribute: ResourceLocation
    action: t.Literal[
        "get",
        "base get",
        "base set",
        "modifier add",
        "modifier revome",
        "modifier value get"
    ]
    scale: float | None
    uuid: UUID | None
    attr_name: str | None
    value: float | None
    operation: t.Literal["add", "multiply", "multiply_base"] | None
    
    @t.overload
    def __init__(self, target: Target, attribute: ResourceLocation, action: t.Literal["get", "base get", "base set", "modifier add", "modifier revome", "modifier value get"]) -> None:
        ...
    
    @t.overload
    def __init__(self, target: Target, attribute: ResourceLocation, action: t.Literal["get", "base get"], scale: float) -> None:
        ...
        
    @t.overload
    def __init__(self, target: Target, attribute: ResourceLocation, action: t.Literal["base set"], value: float) -> None:
        ...
    
    @t.overload
    def __init__(self, target: Target, attribute: ResourceLocation, action: t.Literal["modifier add"], uuid: UUID, name: str, value: float, operation: t.Literal["add", "multiply", "multiply_base"]) -> None:
        ...
    
    @t.overload
    def __init__(self, target: Target, attribute: ResourceLocation, action: t.Literal["modifier remove"], uuid: UUID) -> None:
        ...
        
    @t.overload
    def __init__(self, target: Target, attribute: ResourceLocation, action: t.Literal["modifier value get"], uuid: UUID, scale: float) -> None:
        ...
    
    def __init__(self, target, attribute, action, scale = None, uuid = None, name = None, value = None, operation = None) -> None:
        """Gets or modifies an attribute of target entity

        Args:
            target (Target): The target entity or selector for this command
            attribute (ResourceLocation): The attribute to modify
            action (Literal): Command action
            scale (float, optional): Scales the attribute. Used for some actions.
            uuid (UUID, optional): The UUID of a selected attribute, check the wiki for more informaiton. Used for some actions.
            name (str, optional): The name of the attribute. Used for some actions.
            value (float, optional): The value to give the attribute. Used for some actions.
        """
        self.target = target
        self.attribute = attribute
        self.action = action
        self.scale = scale
        self.uuid = uuid
        self.attr_name = name
        self.value = value
        self.operation = operation
    
    def construct(self) -> str:
        scale = f" {self.scale}" if self.scale else ''
        uuid  = f" {self.uuid}" if self.uuid else ''
        name  = f" {self.attr_name}" if self.attr_name else ''
        value = f" {self.value}" if self.value else ''
        operation = f" {self.operation}" if self.operation else ''
        return f"{self.name} {self.target} {self.attribute} {self.action}{scale}{uuid}{name}{value}{operation}"

class Bossbar(Command):
    
    def __init__(self) -> None:
        """Not implemented

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError


class Clear(Command):
    """Clears target item from player's inventory"""
    
    target: Target
    item: str | None
    count: int | None
    
    @t.overload
    def __init__(self, target: Target) -> None:
        ...
        
    @t.overload
    def __init__(self, target: Target, item: str) -> None:
        ...
    
    @t.overload
    def __init__(self, target: Target, item: str, count: int) -> None:
        ...
    
    def __init__(self, target, item = None, count = None) -> None:
        """Clears target item from player's inventory

        Args:
            target (Target): The target player for the command
            item (str, optional): The select item. Defaults to None.
            count (int, optional): How many of target item to remove from player. Defaults to None.
        """
        self.target = target
        self.item = item
        self.count = count
    
    def construct(self) -> str:
        item = self.if_exists(self.item)
        count = self.if_exists(self.count)
        return f"{self.name} {self.target}{item}{count}"

class Clone(Command):
    """Clones a set of blocks from one location in the world to another. 
        For cross-dimensional cloning, check Clone.From() or Clone.To()"""
    start: BlockPosition
    end: BlockPosition
    position: BlockPosition
    r_type: t.Literal["replace", "masked"]
    behavior: t.Literal["force", "move", "normal"]
    f_tag: str | None
    
    @t.overload
    def __init__(self, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], position: BlockPosition | tuple[int, int, int] | list[int]) -> None:
        ...
    
    @t.overload
    def __init__(self, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], position: BlockPosition | tuple[int, int, int] | list[int], r_type: t.Literal["replace", "masked"], behavior: t.Literal["force", "move", "normal"], filter: str) -> None:
        ...
    
    def __init__(self, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], position: BlockPosition | tuple[int, int, int] | list[int], r_type: str = "replace", behavior: str = "normal", filter: str | None = None) -> None:
        """Clones a set of blocks from one location in the world to another. 
        For cross-dimensional cloning, check Clone.From() or Clone.To()

        Args:
            start (BlockPosition | tuple[int, int, int] | list[int]): The position of the first corner of bounding-box
            end (BlockPosition | tuple[int, int, int] | list[int]): The end position of the bounding box
            position (BlockPosition | tuple[int, int, int] | list[int]): The location to clone to
            r_type (str, optional): The replace type. Defaults to "replace".
            behavior (str, optional): How the command should act. Defaults to "normal".
            filter (str | None, optional): The selected block filter, will override r_type. Defaults to None.
        """
        self.start    = start    if  isinstance(start, BlockPosition)   else BlockPosition(start[0], start[1], start[2])
        self.end      = end      if   isinstance(end, BlockPosition)    else BlockPosition(end[0], end[1], end[2])
        self.position = position if isinstance(position, BlockPosition) else BlockPosition(position[0], position[1], position[2])
        self.r_type   = r_type
        self.behavior = behavior
        self.f_tag    = filter
    
    def construct(self) -> str:
        if self.f_tag:
            middle = f"filter {self.f_tag}"
        else:
            middle = self.r_type
        return f"{self.name} {self.start.cmd_str} {self.end.cmd_str} {self.position.cmd_str} {middle} {self.behavior}"
    
    class From(Command):
        """Clones a set of blocks across dimensions from a set dimensions"""
        
        dimension: str
        start: BlockPosition
        end: BlockPosition
        position: BlockPosition
        r_type: t.Literal["replace", "masked"]
        behavior: t.Literal["force", "move", "normal"]
        f_tag: str | None
        
        @t.overload
        def __init__(self, dimension: str, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], position: BlockPosition | tuple[int, int, int] | list[int]) -> None:
            ...
        
        @t.overload
        def __init__(self, dimension: str, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], position: BlockPosition | tuple[int, int, int] | list[int], r_type: t.Literal["replace", "masked"], behavior: t.Literal["force", "move", "normal"], filter: str) -> None:
            ...
            
        def __init__(self, dimension: str, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], position: BlockPosition | tuple[int, int, int] | list[int], r_type: str = "replace", behavior: str = "normal", filter: str | None = None) -> None:
            """Clones a set of blocks across dimensions

            Args:
                dimension (str): The target dimension to clone from
                start (BlockPosition | tuple[int, int, int] | list[int]): The position of the first corner of bounding-box
                end (BlockPosition | tuple[int, int, int] | list[int]): The end position of the bounding box
                position (BlockPosition | tuple[int, int, int] | list[int]): The location to clone to
                r_type (str, optional): The replace type. Defaults to "replace".
                behavior (str, optional): How the command should act. Defaults to "normal".
                filter (str | None, optional): The selected block filter, will override r_type. Defaults to None.
            """
            self.dimension = dimension
            self.start    = start    if  isinstance(start, BlockPosition)   else BlockPosition(start[0], start[1], start[2])
            self.end      = end      if   isinstance(end, BlockPosition)    else BlockPosition(end[0], end[1], end[2])
            self.position = position if isinstance(position, BlockPosition) else BlockPosition(position[0], position[1], position[2])
            self.r_type   = r_type
            self.behavior = behavior
            self.f_tag    = filter
        
        def construct(self) -> str:
            if self.f_tag:
                middle = f"filter {self.f_tag}"
            else:
                middle = self.r_type
            return f"{self.name} from {self.dimension} {self.start.cmd_str} {self.end.cmd_str} {self.position.cmd_str} {middle} {self.behavior}"
    
    class To(Command):
        """Clones a set of blocks in the origin dimension to another dimension"""
        dimension: str
        start: BlockPosition
        end: BlockPosition
        position: BlockPosition
        r_type: t.Literal["replace", "masked"]
        behavior: t.Literal["force", "move", "normal"]
        f_tag: str | None
        
        @t.overload
        def __init__(self, dimension: str, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], position: BlockPosition | tuple[int, int, int] | list[int]) -> None:
            ...
        
        @t.overload
        def __init__(self, dimension: str, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], position: BlockPosition | tuple[int, int, int] | list[int], r_type: t.Literal["replace", "masked"], behavior: t.Literal["force", "move", "normal"], filter: str) -> None:
            ...
            
        def __init__(self, dimension: str, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], position: BlockPosition | tuple[int, int, int] | list[int], r_type: str = "replace", behavior: str = "normal", filter: str | None = None) -> None:
            """Clones a set of blocks in the origin dimension to another dimension

            Args:
                dimension (str): The target dimension to clone to
                start (BlockPosition | tuple[int, int, int] | list[int]): The position of the first corner of bounding-box
                end (BlockPosition | tuple[int, int, int] | list[int]): The end position of the bounding box
                position (BlockPosition | tuple[int, int, int] | list[int]): The location to clone to
                r_type (str, optional): The replace type. Defaults to "replace".
                behavior (str, optional): How the command should act. Defaults to "normal".
                filter (str | None, optional): The selected block filter, will override r_type. Defaults to None.
            """
            self.dimension = dimension
            self.start    = start    if  isinstance(start, BlockPosition)   else BlockPosition(start[0], start[1], start[2])
            self.end      = end      if   isinstance(end, BlockPosition)    else BlockPosition(end[0], end[1], end[2])
            self.position = position if isinstance(position, BlockPosition) else BlockPosition(position[0], position[1], position[2])
            self.r_type   = r_type
            self.behavior = behavior
            self.f_tag    = filter
        
        def construct(self) -> str:
            if self.f_tag:
                middle = f"filter {self.f_tag}"
            else:
                middle = self.r_type
            return f"{self.name} {self.start.cmd_str} {self.end.cmd_str} to {self.dimension} {self.position.cmd_str} {middle} {self.behavior}"
    
    class FromTo(Command):
        """Clones a set of blocks from a selected dimension to another selected dimension, neither of which are dependent on the origin dimension for the command"""
        start_dim: str
        end_dim: str
        start: BlockPosition
        end: BlockPosition
        position: BlockPosition
        r_type: t.Literal["replace", "masked"]
        behavior: t.Literal["force", "move", "normal"]
        f_tag: str | None
        
        @t.overload
        def __init__(self, start_dim: str, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], end_dim: str, position: BlockPosition | tuple[int, int, int] | list[int]) -> None:
            ...
        
        @t.overload
        def __init__(self, start_dim: str, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], end_dim: str, position: BlockPosition | tuple[int, int, int] | list[int], r_type: t.Literal["replace", "masked"], behavior: t.Literal["force", "move", "normal"], filter: str) -> None:
            ...
        
        def __init__(self, start_dim: str, start: BlockPosition | tuple[int, int, int] | list[int], end: BlockPosition | tuple[int, int, int] | list[int], end_dim: str, position: BlockPosition | tuple[int, int, int] | list[int], r_type: str = "replace", behavior: str = "normal", filter: str | None = None) -> None:
            """Clones a set of blocks from a selected dimension to another selected dimension, neither of which are dependent on the origin dimension for the command

            Args:
                start_dim (str): _description_
                start (BlockPosition | tuple[int, int, int] | list[int]): _description_
                end (BlockPosition | tuple[int, int, int] | list[int]): _description_
                end_dim (str): _description_
                position (BlockPosition | tuple[int, int, int] | list[int]): _description_
                r_type (str, optional): _description_. Defaults to "replace".
                behavior (str, optional): _description_. Defaults to "normal".
                filter (str | None, optional): _description_. Defaults to None.
            """
            self.start_dim = start_dim
            self.end_dim   = end_dim
            self.start     = start    if  isinstance(start, BlockPosition)   else BlockPosition(start[0], start[1], start[2])
            self.end       = end      if   isinstance(end, BlockPosition)    else BlockPosition(end[0], end[1], end[2])
            self.position  = position if isinstance(position, BlockPosition) else BlockPosition(position[0], position[1], position[2])
            self.r_type    = r_type
            self.behavior  = behavior
            self.f_tag     = filter
        
        def construct(self) -> str:
            if self.f_tag:
                middle = f"filter {self.f_tag}"
            else:
                middle = self.r_type
            return f"{self.name} from {self.start_dim} {self.start.cmd_str} {self.end.cmd_str} to {self.end_dim} {self.position.cmd_str} {middle} {self.behavior}"

class Comment(Command):
    
    content: tuple[str]
    
    def __init__(self, *content: str) -> None:
        """Adds a comment to the script"""
        self.content = content

    def construct(self) -> str:
        return f"# {' '.join(self.content)}"
        
    

class Execute(Command):
    
    def __init__(self, *conditionals: str) -> None:
        pass
    
    class Conditional:
        ...
    
    class Align(Conditional):
        ...
        
    class Anchored(Conditional):
        ...
    
    class At(Conditional):
        ...
        
    class As(Conditional):
        ...
    
    class Facing(Conditional):
        ...
    
    class If(Conditional):
        ...
    


# Clean Up Namespace
del t