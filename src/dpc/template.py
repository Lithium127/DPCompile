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

    _identifier: t.Any

    _INSTANCE_REGISTRY: list[Template] = []

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
        pass

    def __init_subclass__(cls):
        true_init = cls.__init__
        def wrapped_init(self, *args, **kwargs):
            true_init(self, *args, **kwargs)
            self.__class__._register_instance(self)
        cls.__init__ = wrapped_init
    
    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if isinstance(value, Script) and BaseCommand._CURRENT_CONTEXT is not None:
            value.method_instance = self
        return value
    
    def to_command_str(self) -> str:
        """Converts this template to a command renderable
        identifier that references the single object that
        this template references.

        Returns:
            str: The identifier for the in-game instance 
                 of this template
        """
        return self.identifier
    
    @classmethod
    def _register_instance(cls, instance: Template) -> None:
        if cls is not Template:
            for base in cls.__bases__:
                if hasattr(base, "_register_instance"):
                    base._register_instance(instance)
        if not cls._registry_has_instance(instance):
            cls._INSTANCE_REGISTRY.append(instance)
    
    @classmethod
    def _registry_has_instance(cls, instance: Template) -> None:
        for item in cls._INSTANCE_REGISTRY:
            if item.identifier == instance.identifier:
                return True
        return False
    
    @classmethod
    def find(cls, identifier: t.Any) -> Template | None:
        """Finds an instance of a template from a given
        identifier.

        If an object with a matching identifier is not 
        found then a blank proxy object is created until
        a real instance is constructed. When an object
        with the same identifier is created, information
        from the properly initialized instance is copied
        to the stored instance that already exists in the
        registry.

        If a proxy object exists in the registry and a
        properly initialized template instance with the
        same identifier is never instanced then an error
        will be thrown during build to avoid errors caused
        by calling template scripts without a proper object

        Args:
            identifier (Any): The identifier to search the class
                              registry for. Note that instances
                              are added to all class registries
                              that they inherit from, as such
                              searching the `Template` base class
                              for an instance will search all created
                              instances. If two instances share the 
                              same identifier the first one created 
                              is returned.

        Returns:
            Template: The instance with a matching identifier. If two
                      instances with the same identifier are in the
                      registry then the one that was added first is
                      returned.
        """
        for item in cls._INSTANCE_REGISTRY:
            if item.identifier == identifier:
                return item
        # Make new instance of class and add to registry with correct title
        instance = cls.__new__(cls)
        instance.identifier = identifier
        cls._register_instance(instance)
        return None
    
    
    @property
    def identifier(self) -> t.Any:
        return self._identifier
    
    @identifier.setter
    def identifier(self, value: t.Any) -> None:
        self._identifier = value




class TemplateDecoratable(ScriptDecoratable):

    def template(self, path: Path | str = None, dev: bool = False) -> callable:
        def inner(cls: type):
            if not issubclass(cls, Template):
                raise TemplateError("Decorated non-template class with template registry.")
            
            # Search class registry for scripts
            for attr in dir(cls):
                value = getattr(cls, attr, None)
                if isinstance(value, Script):
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