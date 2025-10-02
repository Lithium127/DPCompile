from __future__ import annotations
import typing as t
import inspect

from abc import ABCMeta

from pathlib import Path

from .packfile import PackFile, FileParentable
from ..cmd.command import BaseCommand, Comment, CallFunction


class ScriptError(Exception):
    script: Script

    def __init__(self, script: Script = None, *args):
        super().__init__(*args)
        self.script = script


class ScriptContext:
    """Represents the content of a script during rendering"""
    
    _writable: bool
    _script: Script
    data: list[BaseCommand]
    """The ungenerated list of commands that will make up the content of the script"""
    
    def __init__(self, parent: Script):
        self._script = parent
        self.data = []
        self._writable = False
    
    def __enter__(self) -> ScriptContext:
        self._writable = True
        BaseCommand._set_context(self)
        return self
    
    def __exit__(self, exc_type, exc, tb) -> bool:
        # TODO: More verbose script error handling.
        # Currently when there is an error in a script the program
        # suppresses that error until the script builds, and the
        # error appears to be from the script building action.
        # Errors should always point towards a user mistake.
        self._writable = False
        BaseCommand._pop_context()
        if exc:
            new_exc = ScriptError(self.script, f"{exc_type.__name__} while rendering script {self.script.full_name}")
            raise new_exc from exc
        return False
    
    def add_cmd(self, data: t.Any, *, index: int | None = None) -> None:
        """Adds a command to this script information

        Args:
            data (Command): The command to add to this scripts content
            index (int | None, optional): An optional index for this command, 
                                            modifying the position within the 
                                            script. Defaults to None.
        """
        if not self._writable:
            # TODO: Replace with a PackIOException
            raise ValueError("Script context is not yet open")
        
        if index is None:
            self.data.append(data)
        else:
            self.data.insert(index, data)
            
    @property
    def writable(self) -> bool:
        return self._writable
    
    @property
    def script(self) -> Script:
        return self._script

class Script(PackFile):
    """Represents a single `.mcfunction` object within a given datapack"""
    
    _content_func: callable
    _pass_self: bool
    _method_instance: object
    
    _ctx: ScriptContext | None
    
    _is_rendered: bool
    
    _parent: ScriptDecoratable
    _relative_path: Path
    
    def __init__(self, name: str, content: callable | None, *, pass_script: bool = False):
        """Represents a script file within a datapack that can hold commands and operations.
        Each script has the extension `.mcfunction`

        Args:
            pack (PackDSL): The parent pack or module, attributes from this parent will 
                            be pulled to determine the location this file should be created 
                            at, all parents require a `build_dir` attribute that holds a 
                            relative path.
            name (str): The name of this file, with or withour extension. The extension
                        will be overriden to `.mcfunction`
            content (callable | None):  A function that can execute within a ScriptContext
                                        to generate content for this script.
            pass_script (bool, optional):   If this script should pass itself to the function 
                                            that generates its content at render time. 
                                            Defaults to False.
        """
        super().__init__(name)
        self.extension = "mcfunction"
        
        self._content_func = content
        self._pass_self = pass_script
        self._method_instance = None
        self._ctx = None
        self._is_rendered = False
    
    def __call__(self):
        if BaseCommand._CURRENT_CONTEXT is not None and not BaseCommand._CURRENT_CONTEXT is self.ctx:
            # Case for calling within other functions
            if BaseCommand._CURRENT_CONTEXT.script.pack._build_dev or (not self._is_dev):
                return self.get_command()
        # Case for out of context calls
        return self._call_content_function()
    
    def _call_content_function(self) -> t.Any:
        args = []
        if self._method_instance is not None:
            args.append(self._method_instance)
        if self._pass_self:
            args.append(self)
        return self._content_func(*args)
    
    def render(self):
        if not self._is_rendered:
            with self.ctx:
                self() # Call the content function
            self._is_rendered = True
        
        
        content = []
        
        if len(self.ctx.data) > 0:
            content = [
                Comment(f"This script was automatically generated for [{self.pack._pack_name}]").build(),
                Comment(f"MC Version: {self.pack.version} [{self.pack.version.pack_reference}]").build(),
                # Comment(f"File Path: {self._parent}"),
                "", # Blank line for formatting
            ]
            
            script_desc = self._content_func.__doc__
            if script_desc is not None:
                content.pop(-1)
                content.append(Comment(f"---\n{script_desc}").build())
                content.append("")
            
            for cmd in self.ctx.data:
                content.append(cmd.build())
        else:
            content.append(Comment(f"No content generated for {self.full_name}", register = False).build())    
        return "\n".join(content)
    
    def get_command(self) -> CallFunction:
        """Creates and attaches the minecraft 
        executable command that runs this script

        Returns:
            CallFunction: The Command that runs this script
        """
        return CallFunction(self.namespace_name)
    
    @property
    def has_ctx(self) -> None:
        return (self._ctx != None)

    @property
    def ctx(self) -> ScriptContext:
        """Returns or creates the current context attached to this instance.
        
        If this is accessed within a decorated content function the context will
        always exist, meaning content can be forcebly added partway though execution"""
        if not self.has_ctx:
            self._ctx = ScriptContext(self)
        return self._ctx
    
    @property
    def namespace_name(self) -> str:
        return f"{self.pack._namespace}:{self.name}"


class RayCastScript(Script):
    """Represetns a script file that recursively iterates until either 
    a depth limit is reached or an end condition is true."""

    max_depth: int

    def __init__(self, name, content, depth: int, *, pass_script = False):
        """_summary_

        Args:
            name (_type_): _description_
            content (_type_): _description_
            depth (int): _description_
            pass_script (bool, optional): _description_. Defaults to False.
        """
        super().__init__(name, content, pass_script=pass_script)
        self.max_depth = depth
    
    def stop():
        """Signals the Recursive script to halt iteration

        Returns:
            BaseCommand: The command that halts iteration
        """
        return Comment("This is a comment...")

# TODO: Update storage method for scripts, as modules should be able to attach scripts directly without needing a parent
class ScriptDecoratable(FileParentable, metaclass=ABCMeta):
    """An abstract class that provides an object with
    a decorator that turns a function into the content
    of a managed script.
    
    This will make
    
    Usage:
    ```python
    class Module(ScriptDecoratable):
        # Other code for this object
        ...
    inst = Module(...) # Create instance
    
    @inst.mcfn(<args>)
    def script():
        return ...
    ```
    """
    
    _script_collectors: list[Script]
    
    def __init__(self):
        super().__init__()
        self._script_collectors = []
    
    def mcfn(self, name: str = None, *, dev: bool = False, sort: t.Literal['tick', 'load'] | None = None) -> callable:
        """Decorates a function to create a script.
        Adds a `.mcfunction` file, or `script`, to the parent object's collectors 
        attribute.
        
        This decorator must always be called fully, as even without arguments
        the decorator returns an inner function.
        
        The function being decorated should optionally take in the script instance
        that the function is contained within, used for context management.
        
        The decorated functions type will be overriden to a type of `Script`.
        
        The first argument of the function, if it exists, and is not annotated as
        anything other than type `Script`, will have the script instance that
        wraps the decorated function passed into the function, allowing for access
        to global contexts at compile time.
        
        ### Basic example
        ```python
        with PackDSL(...) as pack:
            @pack.mcfn()
            def foo():
                cmd.Comment("Test comment")
        ```
        
        ### Example with script
        ```python
        with PackDSL(...) as pack:
            @pack.mcfn(name = "initialization")
            def foo(script: Script):
                # Pack is accessable through script parent
                cmd.Comment(f"This comment is from {script.full_name}")
        ```
        
        The function that is wrapped will be executed within a script context and
        all command that are initialized within that context will be registered with
        that context to be compiled and writted to a script file. If a command is 
        created outside of the active function that is being wrapped, it can be added
        to the current context at any time within the wrapped function with a call to
        the context's `add_cmd()` method
        
        ```python
        with PackDSL(...) as pack:
            # Create command instance outside of function
            outside_cmd = cmd.Command("This was created outside the wrapped function")
            @pack.mcfn()
            def test(script):
                cmd.Command(f"Created inside {script.full_name}")
                # Add external command to script
                script.ctx.add_cmd(outside_cmd)
        ```
        
        Running this generates the following:
        ```Created inside test.mcfunction
        This was created outside the wrapped function
        ```
        
        ### Docstring Identification
        The script that is created by this decorator will take the docstring from the
        wrapped function and add it at the top of the generated file.
        
        ```python
        with PackDSL(...) as pack:
            
            @pack.mcfn()
            def test(script):
                \"\"\"This docstring will be added to the top of the file\"\"\"
                ...
            
            @pack.mcfn(desc = "Overriden description")
            def override():
                \"\"\"This docstring will not be used because of the argument\"\"\"
                ...
        ```
        
        This will add the docstring directly to the generated script. Unless the docstring 
        is overriden by the argument to the `mcfn` decorator. The overriden description is
        directly written to the `__doc__` attribute of the internal function.

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

        Returns:
            Script: The new script instance that wraps the function passed
        """
        
        def inner(func: function) -> callable:
            script = self.create_script_from_callable(func, name=name, dev=dev)
            is_ticking = None if sort is None else (sort == 'tick')
            self.add_script(script, ticking=is_ticking)
            return script
        return inner
    
    def mcraycast(self, name: str = None, *, desc: str = None, dev: bool = False) -> callable:
        
        def inner(func: function) -> callable:
            
            script = self.create_script_from_callable(func, name=name)
            
            script._is_dev = dev
            
            # Raycast scripts can never implicitly be ticking or loading
            self.add_script(script=script, ticking=None)
            
            return script
        return inner
    
    def add_script(self, script: Script, ticking: bool | None, *, alternate_path: str = "") -> None:
        """Adds a given script instance to this objects
        registry.

        Args:
            script (Script): The script object to add
        """
        
        script._parent = self
        self._pack_reference.register_file(
            f"data/{self._pack_reference._namespace}/function{'/'+alternate_path if len(alternate_path) > 0 else ''}",
            script
        )
        if ticking is not None:
            self._pack_reference.add_script_to_taglist(
                script=script,
                sort = 'tick' if ticking else 'load'
            )
        # Renders the script proactively for scoreboard discovery
        self._script_collectors.append(script)
    
    def _prerender_scripts(self) -> None:
        """Internal function to render all scripts
        attached to this object at once to resolve
        pathing conflicts and obtain scoreboards.
        
        Also pre-renders modules and attaches the
        scripts contained to the pack directory
        """
        for script in self._script_collectors:
            script.render()
    
    def create_script_from_callable(self, func: callable, *, name: str = None, dev: bool = False,  instance: object = None) -> Script:
        """Creates a new script instance by observing the attributes of
        a given function. The function is run each time the script is rendered

        Args:
            func (callable): The function that creates the content of the script
            name (str, optional): The optional overriden name for the script. Defaults to None.

        Returns:
            Script: The new script instance
        """
        args = inspect.getfullargspec(func)
        pass_script = False
        if len(args.args) >= 1:
            # Get type if available otherwise set to true
            if instance is None or len(args.args) >= 2:
                pass_script = args.annotations.get(args.args[0], Script) is Script
                
        
        script = Script(
            name = name or func.__name__,
            content = func,
            pass_script=pass_script
        )
        script._is_dev = dev
        script._method_instance = instance
        return script
        