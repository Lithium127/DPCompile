from __future__ import annotations
import typing as t

from .IO.script import Script, ScriptDecoratable, create_script_from_callable
from pathlib import Path

from .cmd import CallFunction
from .cmd.bases import BaseCommand
from .datatypes import mctype

def script(
        name: str = None, 
        *, 
        dev: bool = False, 
        sort: t.Literal['tick', 'load'] | None = None,
        path: Path | str = None,
        mask_if_empty: bool = True
        ):
    """Makes a template method into a script instance that
    can be added to a given pack. See `ScriptDecoratable.mcfn()` 
    for more information.

    Args:
        name (str, optional):   The optional name for this script, if no name is given 
                                the name is interpreted from the name of the function. 
                                Defaults to None.
        dev (bool, optional):   If this script is intended to exist only as a 
                                developmental tool for this pack. If set to `True` 
                                then this script will be omitted from the final
                                compilation if the pack is in any mode but development.
                                Defaults to False.
        sort (['tick', 'load'] | None, optional): If this script should be run each 
                                game rick or on pack load. If `None` then the script 
                                is not called in either case. 
                                Defaults to None.
        path (Path | str, optional): An alternate path for this script to be added to. 
                                If the path starts with a "/" then it will be added 
                                relative to pack root, otherwise the file will be added 
                                relative to the template's file path. 
                                Defaults to None.
    """
    def inner(func: function) -> callable:
        script = create_script_from_callable(func, name=name, dev=dev)
        script.is_ticking = None if sort is None else (sort == 'tick')
        script.alternate_path = path or ""
        script._mask_on_empty = mask_if_empty
        return script # Scripts will be added to pack later
    return inner

class TemplateError(Exception):
    pass

class TemplateMeta(type):

    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if isinstance(value, Script):
            value._method_instance
        return value

class Template:
    """A `Template` is the implementation of classes within a 
    datapack. A template defines a set of scripts and data
    attached to an object in the game that can be referenced
    by any identifier. This acts as a collection of reusable
    code that can be run by different objects.

    Templates define scripts that access and modify in-game 
    objects. In these methods the `self` variable is acts as
    the partially-constructed instance, as most specific data
    from within the game is not directly accessable.

    ```python
    @pack.template()
    class Example(Template):
        
        @script()
        def summon(self):
            ...
    ```
    """

    def __init__(self):
        """Returns the instance of this class 
        with attached identifying information
        to reference the conjoined template
        instance in the game world, implementing 
        any required logic to locate a given 
        object in the world using entity 
        selectors.

        An example would be returning the required 
        search through player `NBT` data to locate 
        a single item that matches the required 
        template to then run scripts with that object

        Args:
            identifier (t.Any): The descriptor that identifies objects 
                                that match this template in the game world.
        """
    
    def to_command_str(self) -> str:
        """Converts this template to a command renderable
        identifier that references the single object that
        this template references.

        Returns:
            str: The identifier for the in-game instance 
                 of this template
        """
        return self.identifier
    
    def _identifier(self) -> mctype:
        return None

    @property
    def identifier(self) -> mctype:
        return self._identifier()

class TemplateDecoratable(ScriptDecoratable):

    def template(self, path: Path | str = None, dev: bool = False) -> callable:
        def inner(cls: type):
            if not issubclass(cls, Template):
                raise TemplateError("Decorated non-template class with template registry.")
            
            # Search class registry for scripts
            for attr in dir(cls):
                value = getattr(cls, attr, None)
                if isinstance(value, Script):
                    value.method_instance = cls()
                    if dev:
                        value._is_dev = dev
                    alternate_path = getattr(value, "alternate_path", "")
                    if not alternate_path.startswith("/"):
                        alternate_path = f"{path}/{alternate_path}"
                    self.add_script(
                        value, 
                        getattr(value, "is_ticking", None), 
                        alternate_path=alternate_path.lstrip("/")
                    )
            return cls
        return inner