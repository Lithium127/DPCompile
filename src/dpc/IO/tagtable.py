from __future__ import annotations
import typing as t
from abc import ABCMeta

import json

from .packfile import FileParentable

from .jsonfile import JsonFile
from .packfile import PackFile

if t.TYPE_CHECKING:
    from ..packdsl import PackDSL

# TODO: Instance tables from the game, such as #minecraft:burnable_logs

class TagTable(JsonFile):
    """Represents a table of namespace organized, path locatable
    minecraft datatypes that can be interpreted by internal systems,
    structures, and functions to implement custom behaviour.
    
    TagTables are iterable, they will iterate through each entry
    they contain, presenting the pure value at that location."""
    
    _namespace: str
    _entries: list[str]
    _sort: str
    replace: bool
    
    def __init__(self, sort: t.Literal['block', 'function'], name: str, entries: list[str] | None = None, *, namespace: str | None = None, replace: bool = False, indent: int = 4):
        """Represents a table of tagged datatypes that can be referenced by
        functions and commands within a datapack. Tables can include
        refernces to other tables, as well as blocks and entities
        from any mods or other sources as long as a namespace can
        be referenced.
        
        Building tables will automatically be attached to the
        `data/<namespace>/tags/<table_type>` directory and will
        result in a literal representation of each of the enteries
        contained denoted by path and namespace within a `.json`
        file.
        ```
        values : [
            "minecraft:stone",
            "minecraft:smooth_stone",
            ...
            // Further entries
        ]
        ```
        
        The game uses tables in different places, denoting block
        and entity types, structure lists, and what functions to 
        run on load and each tick. Therefore the table datatype
        includes a type identifier that is used to determine what
        directory within the pack file system the table will be
        generated in. The directory choice is shown below
        ```
        <root>/data/<namespace>/tags/<type>/<name>.json
        ```
        
        Tables will server their namespace given name when passed
        to the entry list of another table, and blocks follow the
        same principle.

        Args:
            sort ("block", "function"): The content type that this table contains.
                                        Also determines the location of this file 
                                        within the pack scope.
            name (str): The name of this table, dictates the name of the file
            entries (list[str] | None, optional): The list of entries within this table, 
                                                  each must reference a real, existing 
                                                  minecraft or pack type or table. 
                                                  Defaults to None.
            namespace (str | None, optional): The optional namespace for this table. 
                                              If no namespace is given the namespace 
                                              is interpreted from the pack parent. 
                                              Defaults to None.
            replace (bool, optional): If this file should replace other files with the
                                      same name in any pack. Defaults to False
            indent (int, optional): The optional indent for this file, 
                                    inherited from `JsonFile`. Purely 
                                    visual. Defaults to 4.
        """
        super().__init__(name, indent=indent)
        self._namespace = namespace
        self._sort = sort
        self.replace = replace
        self._entries = entries or []
    
    def __iter__(self) -> t.Iterator[str]:
        return iter(self._values)
    
    @classmethod
    def block_table(cls, name: str, entries: list[str] | None = None, *, namespace: str | None = None, replace: bool = False, indent: int = 4):
        instance = super().__new__(cls)
        instance.__init__('block', entries, namespace=namespace, replace=replace, indent=indent)
        return instance
    
    @classmethod
    def block_table(cls, name: str, entries: list[str] | None = None, *, namespace: str | None = None, replace: bool = False, indent: int = 4):
        instance = super().__new__(cls)
        instance.__init__('function', entries, namespace=namespace, replace=replace, indent=indent)
        return instance
    
    @property
    def namespace(self) -> str:
        return self._namespace or self.pack._namespace
    
    @namespace.setter
    def namespace(self, value: str) -> None:
        self._namespace = value
    
    @property
    def table_tag(self) -> str:
        return f"#{self.namespace}:{self.name}"
    
    @property
    def sort(self) -> str:
        return self._sort
    
    def _get_namespace_names(self) -> list[str]:
        content = []
        for item in self._entries:
            if isinstance(item, TagTable):
                content.append(item.table_tag)
                continue
            if isinstance(item, PackFile):
                content.append(f"{item.pack._namespace}:{item.name}")
                continue
            content.append(item)
        return content
    
    def render(self):
        data = {
            "values" : self._get_namespace_names()
        }
        if self.replace:
            data["replace"] = False
        return json.dumps(data, indent=self.indent)
