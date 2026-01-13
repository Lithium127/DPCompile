from __future__ import annotations
import typing as t

from .version import VersionRange

from .mctype import MinecraftType

class Entity(MinecraftType):
    
    id: int
    namespace: str
    name: str
    display_name: str
    category: str
    version: VersionRange

    @t.overload
    def __init__(self, name: str, /) -> None: ...

    def __init__(self,
                 name: str,
                 *,
                 id: int = None,
                 namespace: str | None = None,
                 display_name: str = None,
                 category: str = None,
                 width: float = None,
                 height: float = None,
                 versions: VersionRange | tuple[str, str] = None
                 ):
        """Represents an entity within the game world without position or any other
        game-based information. Note that instances do not describe a single entity
        but all entities of its specified type. Ex: `Entitys.PIG` describes *all*
        pigs in the world. To narrow the selection call the Entity instance or see
        the EntitySelector type.

        Entities are not intended to be instanced directly. See the `Entitys` enum
        for pre-generated entities. If making a mod compatability, instance entities
        with required information.

        Args:
            name (str): The name of this entity. Can include a namespace which will be
                        used *if* the namespace argument is not specified.
            id (int, optional): The internal in-game identification number for this type 
                                of entity. Defaults to None.
            namespace (str | None, optional): The namespace this entity is a part of. If 
                                              not specified it is interpreted from the 
                                              entity name, otherwise defaults to 
                                              'minecraft'. Defaults to None.
            display_name (str, optional): The display name for this entity. Not used 
                                          directly for commands, however this is the 
                                          accurate in-game name for entities of this 
                                          type. Defaults to None.
            category (str, optional): The category this entity is a part of. Defaults to
                                      None.
            width (float, optional): The width of this entity's hitbox. Defaults to None.
            height (float, optional): The height of this entity's hitbox. Defaults to 
                                      None.
            versions (VersionRange | tuple[str, str], optional): The range of versions 
                                            that this entity exists in. Defaults to None.
        """
        if (":" in name) and (namespace is None):
            namespace, name = name.split(":")[:2]
        self.name = name
        self.namespace = namespace or 'minecraft'
        self.display_name = display_name
        self.id = id
        
        self.category = category
        self.bbox = (width, height)

        if versions is not None:
            self.version = versions if isinstance(versions, VersionRange) else VersionRange(*versions)
        else:
            self.version = VersionRange.largest()
    
    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self, value):
        if not isinstance(value, Entity):
            return False
        return self.id == value.id
    
    def __call__(self) -> Selector: ...

    def to_command_str(self):
        return f"{self.namespace}:{self.name}"
    
    def nearest(self) -> Selector: ...

    @property
    def width(self) -> float:
        return self.bbox[0]
    
    @property
    def height(self) -> float:
        return self.bbox[1]




SelectorLiteral = t.Literal["e", "a", "r", "p", "s", "n"]
PlayerSelectorLiteral = t.Literal["a", "r", "p", "s"]
player_selectors = ["a", "r", "p"]


class Selector(MinecraftType):
    """Representation of a selection of entities within the minecraft world.
    Selectors can be filtered by a conditions list to limit the number of
    entities selected.
    
    To see possible options for selectors, look at the `SelectorGroup` enum or
    use the class methods shortcuts.
    
    """
    
    _target: SelectorLiteral
    
    def __init__(self, target: SelectorLiteral):
        self.target = target.lstrip("@") # Remove any user-given prefix
    
    def __call__(self, *arguments) -> ConditionalSelector:
        return ConditionalSelector(self, *arguments)
    
    @property
    def target(self) -> str:
        return self._target
    
    @target.setter
    def target(self, value: str) -> None:
        self._target = value
    
    def targets_player(self, *, strong: bool = False) -> bool:
        return self._target in player_selectors or (self._target == "s" and not strong)
    
    def to_command_str(self):
        return f"@{self._target}"

class PlayerSelector(Selector):
    """A type of selector that only applies to players. Targets will never be anything other than a player. 
    Calling the PlayerSelector with the `type` argument will cause an error to be thrown"""

class ConditionalSelector(Selector):
    """A sub-type of Selector that narrows the search parameters."""

    def __init__(self, target : Selector | SelectorLiteral, *arguments):
        self._target = target

    def __call__(self): pass

    def targets_player(self, *, strong = False):
        return super().targets_player(strong=strong)

    def to_command_str(self):
        return f"{super().to_command_str()}[]"

from .enum.metaenum import EnumMeta

class SelectorEnum(metaclass = EnumMeta[Selector]):
    E: Selector = {"target" : "e"}
    """Selects all alive entities (including players) in loaded chunks."""
    A: PlayerSelector = {"target" : "a"}
    """Selects every player, alive or not."""
    R: PlayerSelector = {"target" : "r"}
    """Selects a random player. To select a random entity, see `SelectorEnum.E(sort=random)`"""
    P: PlayerSelector = {"target" : "p"}
    """Selects the nearest player from the command's execution. If there are multiple nearest 
    players, caused by them being precisely the same distance away, the player who most recently 
    joined the server is selected."""
    S: Selector = {"target" : "s"}
    """Selects the entity (alive or not) that executed the command. It does not select anything 
    if the command was run by a command block or server console. This is considered a player
    targeting instance, however strong player targeting commands will not interpret this selector
    unless the player type is specified as a condition."""
    N: Selector = {"target" : "n"}
    """Selects the nearest entity. It is recomended to use `S.E(sort=nearest)` due to version constraints"""

def ensure_selector(target: str | Selector) -> Selector:
    """Ensures that a given argument is a selector by
    converting single character string values into
    a selection

    Args:
        target (str | Selector): The value to validate

    Returns:
        Selector: The selector instance
    """
    if isinstance(target, Selector):
        return target
    
    if not isinstance(target, str):
        target = str(target)
    target.lstrip("@")
    value = Selector(target[0])
    if target[0] in player_selectors:
        value = PlayerSelector(target[0])
    if "[" in target:
        return value() # Include split arguments for selector
    return value