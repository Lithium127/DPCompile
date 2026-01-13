from __future__ import annotations
import typing as t

from .version import VersionRange

from .mctype import MinecraftType

from ..IO.tagtable import TagTable


class Block(MinecraftType):
    
    id: int
    namespace: str
    name: str
    display_name: str
    hardness: float
    version: VersionRange
    
    @t.overload
    def __init__(self, name: str, /) -> None: ...

    def __init__(self, 
                 name: str, 
                 *, 
                 id: int = None, 
                 namespace: str | None = None, 
                 display_name: str = None, 
                 hardness: float = None,
                 versions: VersionRange | tuple[str, str] = None
                 ) -> None:
        """Represents a single block type within the game. Without a position or other
        game-based information. The namespace defaults to 'minecraft', however can be
        passed in the constructor. If the namespace is not overriden but the name
        argument contains a ':' character (ex: `'arbitrary:blockname'`), the namespace
        is interpreted from the first part of the name.

        Args:
            name (str): The name of the block, can include the namespace which will be
                        used as long as a namespace is not passed
            namespace (str | None, optional): The namespace for this block, interpreted 
                                              from name and will default to 'minecraft' 
                                              is none is given. Defaults to None.
        """
        if (":" in name) and (namespace is None):
            namespace, name = name.split(":")[:2]
        self.name = name
        self.namespace = namespace or 'minecraft'
        self.display_name = display_name
        self.id = id
        self.hardness = hardness
        if versions is not None:
            self.version = versions if isinstance(versions, VersionRange) else VersionRange(*versions)
        else:
            self.version = VersionRange.largest()
    
    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self, value):
        if not isinstance(value, Block):
            return False
        return self.id == value.id
    
    def __call__(self, state: dict[str, t.Any] = None, tags: dict[str, t.Any] = None) -> BlockState:
        return BlockState(self, state, tags)
    
    def to_command_str(self):
        return f"{self.namespace}:{self.name}"


class BlockState(MinecraftType):
    """A type describing a block with 
    a given state or data. Such as `minecraft:stone[foo=bar]`
    or `stone[foo=bar]{baz:nbt}`
    """

    target: Block
    _block_state: dict[str, t.Any] | None
    _data_tags: dict[str, t.Any] | None

    # TODO: Replace `t.Any` in block_state with typevar from block definition
    def __init__(self, block: Block, /, state: dict[str, t.Any] = None, tags: dict[str, t.Any] = None):
        """A type describing a block with a given state or data. Such as `minecraft:stone[foo=bar]`
        or `stone[foo=bar]{baz:nbt}`.

        Args:
            block (Block): The block instance with this data
            state (dict[str, t.Any], optional): The optional state of the block. Not all blocks have available states. Defaults to None.
            tags (dict[str, t.Any], optional): The optional data tags describing this block. Not all blocks have data that can be stored. Defaults to None.
        """
        self.block = block
        self.block_state = state
        self.data_tags = tags
    

    def to_command_str(self):
        value = f"{self.target.to_command_str()}"
        if self.block_state is not None:
            value = value + "[" + " ".join((f"{key}={val}" for key, val in self.block_state.items())) + "]"
        if self.data_tags is not None:
            value = value + "{" + (f"{key}:{val.to_command_str() if hasattr(val, "to_command_str") else str(val)}" for key, val in self._data_tags.items()) + "}"
        return value


    def _validate_target_state(self) -> None:
        if not isinstance(self.target, Block):
            raise ValueError(f"Invalid argument passed to {type(self)}, {type(self.target)} is not of type Block")


    @property
    def block(self) -> Block:
        return self.target
    
    @block.setter
    def block(self, value: Block) -> None:
        self.target = value
        self._validate_target_state()


class BlockPredicate(BlockState):
    """A more advanced type describing a block or table with 
    a given state or data. Such as `minecraft:stone[foo=bar]`
    or `stone[foo=bar]{baz:nbt}`. Unlike the `BlockState` this 
    type can reference tables with data or properties.
    """
    target: Block | TagTable

    def __init__(self, block: Block | TagTable, /, state = None, tags = None):
        super().__init__(block, state, tags)

    def _validate_target_state(self):
        if isinstance(self.target, Block): 
            return # Check if block has allowed states
        if isinstance(self.target, TagTable):
            return # Check if all blocks have allowed states
        raise ValueError(f"Invalid argument passed to {type(self)}, {type(self.target)} is not of type (Block, TagTable)")