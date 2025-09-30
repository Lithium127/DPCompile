from __future__ import annotations
import typing as t
import os

import inspect

from .IO.script import ScriptDecoratable, Script

if t.TYPE_CHECKING:
    from .packdsl import PackDSL


def modulemethod(name: str = None, *, dev: bool = False, sort: t.Literal['tick', 'load'] | None = None):
    """Decorator that marks a module method as a script to be collected
    and interpreted as a file within the pack. Each instance of a module
    will create all scripts that are contained within it

    Args:
            name (str, optional):   The name of the script, if no name is given 
                                    then the name is interpreted from the name 
                                    of the function. 
                                    Defaults to None.
            dev (bool, optional):   If this script is intended to exist only as
                                    a developmental tool for this pack. If set
                                    to true then when the pack build state is
                                    set to anything other than `dev` this script
                                    will skip the compilation step. 
                                    Defaults to False
            sort (['tick', 'load'], optional): Set if this script should be run each
                                    game tick or on pack load. If `None` then then
                                    the script is not called in either case.
                                    Defaults to None
    """
    def decorator(func):
        func._is_mcfn = True  # Mark this method for collection
        func._mcfn_args = { # Attach arguments
            "name" : name,
            "dev" : dev,
            "sort" : sort
        }
        return func
    return decorator

class Module(ScriptDecoratable):
    """The superclass for mountable modules, enabling object-oriented programming
    in datapack code."""
    
    _parent: PackDSL | Module
    _root_dir: str
    _module_name: str
    
    _scripts_collected: bool
    
    def __init__(self, name: str):
        super().__init__()
        self._parent = None
        self._root_dir = ""
        self._module_name = name
        self._scripts_collected = False
    
    def _collect_scripts(self) -> None:
        if not self._scripts_collected:
            for name, member in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
                if getattr(member, "_is_mcfn", False):
                    member_args = getattr(member, "_mcfn_args")
                    # Create and attach known scripts
                    # Note that the module is also able to decorate standard scripts.
                    script = self.create_script_from_callable(
                        member, 
                        name=member_args["name"], 
                        dev=member_args["dev"],
                        instance=self
                    )
                    self.add_script(
                        script, 
                        None if member_args["sort"] is None else (member_args["sort"] == 'tick'),
                        alternate_path=self.module_path
                    )
                    self.__setattr__(name, script)

        self._scripts_collected = True
    
    def build(self) -> None:
        # Defer script collection until
        self._collect_scripts()
    
    @property
    def parent(self) -> PackDSL | Module:
        return self._parent
    
    @property
    def _pack_reference(self) -> PackDSL:
        return self.parent._pack_reference
    
    @property
    def _file_root(self) -> str:
        return os.path.join(self.parent._file_root, self._root_dir, self._module_name)
    
    @property
    def module_path(self) -> str:
        if isinstance(self.parent, Module):
            return f"{self.parent.module_path}/{self._root_dir + '/' if len(self._root_dir) > 0 else ''}{self._module_name}"
        return f"{self._root_dir + '/' if len(self._root_dir) > 0 else ''}{self._module_name}"
    
    def _prerender_scripts(self):
        self._collect_scripts()
        super()._prerender_scripts()