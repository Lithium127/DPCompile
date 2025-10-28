from __future__ import annotations
import typing as t

import json

from .mctype import MinecraftType

class ItemData(MinecraftType):
    """A class to represent item specific NBT data.
    
    Data is not typed outright, and instead is a definition
    of json tags that define what the item is. A common representation
    in a command is as follows.
    ```
    {
        "Item" : {
            "id" : "minecraft:air",
            "count" : 64,
            "nbt" : {...}
        }
    }
    ```
    """

    id: str
    count: int
    data: dict

    def __init__(self, id: str | Item, count: int, data: dict = None):
        self.id = id.id if isinstance(id, Item) else id
        self.count = count
        self.data = data
        
    
    def to_command_str(self):
        inner = f'"id":{self.id}, "count":{self.count}'
        if self.data is not None:
            inner += f', "data": {self.data}'
        return "{" + inner + "}"

class Item(MinecraftType):
    """Represents an item within the game minecraft.
    
    ```python
    Items.IRON_INGOT # Item(id = ..., name = "minecraft:iron_ingot", display)
    ```"""

    namespace: str
    id: str
    display_name: str
    item_number: int

    def __init__(self, id: str, *, item_number: int = None, display_name: str = None, namespace: str = None):
        """Initializes a new item representation. For vanilla minecraft datapacks,
        items are recomended to be accessed from the `Items` enum where all
        attributes are pre-generated.

        For adding modded items to the datapack registry, instance a new item

        Args:
            id (str): The id of the item as a string without a namespace, ex: `"iron_ingot"`
            item_number (int, optional): The integer representation of this object. Used for versions before 1.13. Defaults to None.
            display_name (str, optional): The display name for this item. Defaults to None.
            namespace (str, optional): The namespace this item exists within. Defaults to None.
        """
        if ":" in id:
            id_values = id.split(":")
            namespace = namespace or id_values[0]
            id = id[1]
        self.namespace = namespace or "minecraft"
        self.id = id
        self.item_number = item_number
        self.display_name = display_name
    
    def __call__(self, count: int = 1, data: dict = None) -> ItemData:
        """Converts this item to an `ItemData` object that encodes
        the number of items and the data attached to that item.

        Args:
            count (int, optional): The number of this item that is encoded. Defaults to 1.
            data (dict, optional): The optional NBT data attached to this item. Defaults to None.

        Returns:
            ItemData: The `ItemData` object representing this item
        """
        return ItemData(self, count, data)

    def to_command_str(self):
        return f"{self.namespace}:{self.id}"