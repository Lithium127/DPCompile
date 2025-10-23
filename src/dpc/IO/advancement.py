from __future__ import annotations
import typing as t

import json
import inspect

from .jsonfile import JsonFile
from ..datatypes.textelement import to_textelement

if t.TYPE_CHECKING:
    from ..datatypes.textelement import TextElement
    from ..datatypes.block import Block
    from .script import Script


FrameTypes = t.Literal["challenge", "goal", "task"]

class AdvancementTrigger():
    pass

class AdvancementRewards():
    """A class representing rewards given when
    an advancement is obtained"""

    recipies: list[str]
    loot_tables: list[str]
    experience: int
    script: str | Script

    def __init__(self,
                 recipies: list[str] | str = None,
                 loot_tables: list[str] | str = None,
                 experience: int = None,
                 script: str | Script = None
                 ):
        pass

    def add_recipie(self, *path: str) -> None:
        """Adds recipies given to the
        rewards when a player obtains
        this acheivment.
        """
        for entry in path:
            # Validate that each item is a valid path
            self.recipies.append(entry)
    
    def add_loot_table(self, *path: str) -> None:
        """Adds loot tables to grant
        player items from when this
        advancement is obtained.
        """
        for entry in path:
            self.loot_tables.append(entry)
    
    def set_experience(self, value: int) -> None:
        """Sets the amount of experience given
        when a player obtains this advancement.

        Args:
            value (int): The amount of experience gained.
        """
        self.experience = int(value)
    
    def set_script(self, script: Script | str) -> None:
        """Sets a given script to run when
        this advancement is obtained.

        Args:
            script (Script | str): The script object or final path to that script.
        """
        self.script = script

class Advancement(JsonFile):
    """Represents an advancement that the player
    can achieve within the game.
    
    Advancement can be created either as an instance, or
    through the use of the @mc_advancement decorator.
    """

    _icon: list[str, t.Any]
    frame: FrameTypes
    name: str

    title: TextElement
    description: TextElement | None
    trigger: AdvancementTrigger
    parent: Advancement | str | None
    background: str
    show_toast: bool
    announce_to_chat: bool
    hidden: bool
    sends_telemetry_event: bool

    _rewards: AdvancementRewards
    _func: callable | None
    
    def __init__(self, name: str, 
                       title: str | TextElement, 
                       desc: str | TextElement, 
                       trigger: AdvancementTrigger,
                       icon_item_id: str = "minecraft:barrier",
                       *, 
                       icon_item_nbt: dict | None = None, 
                       frame: FrameTypes = "task", 
                       parent: Advancement | str = None,
                       background: str = None,
                       show_toast: bool = True,
                       announce_to_chat: bool = True,
                       hidden: bool = False,
                       sends_telemetry_event: bool = False,
                ):
        """Creates an advancement file for rendering within the
        pack it gets attached to. Advancements define player
        milestones and events that require contitions to be run.

        Args:
            name (str): The file name for this advancement. Spaces not permitted 
                        and lowercase naming enforced.
            title (str | TextElement): The display title for this advancement as 
                                       a text element.
            desc (str | TextElement): The display description for this advancement 
                                      as a text element or array.
            trigger (AdvancementTrigger): The trigger for this advancement
            icon_item_id (str, optional): The item id for the icon of this 
                                          advancement. Defaults to "minecraft:barrier".
            icon_item_nbt (dict | None, optional): Optional data for the icon item. 
                                                   Defaults to None.
            frame (FrameTypes, optional): The type of frame that the icon will have 
                                          in the advancement window. Defaults to "task".
            parent (Advancement | str, optional): The parent of this advancement. If 
                                                  None, this advancement is interpreted 
                                                  as the root of a catagory. Defaults to 
                                                  None.
            background (str, optional): The path to the background texture of this 
                                        category. Defaults to None.
            show_toast (bool, optional): If this advancement will show a toast popup 
                                         when the player obtains it. Defaults to True.
            announce_to_chat (bool, optional): If this advancement should be announced 
                                               to global chat when a player obtains it. 
                                               Defaults to True.
            hidden (bool, optional): If this advancement is hidden in the advancement 
                                     view. Defaults to False.
            sends_telemetry_event (bool, optional): If this advancement should send 
                                                    telemetry data. Defaults to False.
        """
        super().__init__(name)
        self.name        = name.replace(" ", "_").lower()
        self.title       = to_textelement(title)
        self.description = to_textelement(desc)
        self.icon = [
            icon_item_id,
            icon_item_nbt
        ]
        self.trigger    = trigger
        self.frame      = frame
        self.parent     = parent or None
        self.background = background

        self.show_toast            = show_toast
        self.announce_to_chat      = announce_to_chat
        self.hidden                = hidden
        self.sends_telemetry_event = sends_telemetry_event

        self._rewards = AdvancementRewards()
        self._func = None

    
    def render(self):
        if self._func is not None:
            self._func(self)
        return json.dumps({"nothing":"nothing"})
    
    @property
    def icon_item_id(self) -> str:
        return self._icon[0]
    
    @icon_item_id.setter
    def icon_item_id(self, value: str) -> None:
        self._icon[0] = value

    @property
    def icon_item_nbt(self) -> dict:
        return self._icon[1]
    
    @icon_item_nbt.setter
    def icon_item_nbt(self, value: t.Any) -> None:
        self._icon[1] = value
    
    @property
    def rewards(self) -> AdvancementRewards:
        if not hasattr(self, "_rewards"):
            self._rewards = AdvancementRewards()
        return self._rewards


def mc_advancement(name: str = None, desc: str | TextElement = None, title: str | TextElement = None):
    """System for generating advancement from
    functions that modify an instances content.

    ```python
    @mc_advancement()
    def <advancement_name>(adv) -> None:
        \"\"\"<advancement_description>\"\"\"
        adv.add_triggers("tick", "something else")
        adv.icon = Blocks.STONE # Convert block to icon

    ```

    """

    def inner(func: callable):
        instance = Advancement.__new__(Advancement)
        instance.__init__(
            name    = name or func.__name__,
            title   = to_textelement(title),
            desc    = to_textelement(desc or func.__doc__),
            trigger = None # This will throw error if not overriden
        )

        # Optionally generate content
        instance._func = func
        return instance
    return inner