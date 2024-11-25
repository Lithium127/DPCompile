import os
import typing as t

import contextlib
import shutil
import json

from .exception import DatapackException 
from .shared import DirectoryFlags, PackFile

from .scripts import Module, Script
from .command import Command

from . import constants as const
class Datapack:
    """Represents a de-compiled datapack"""
    
    _pack_name: str
    _namespace: str
    
    _description: str
    
    _target_path: os.PathLike
    _target_version: str
    
    _dir_flags: DirectoryFlags
    
    _script_modules: list[Module]
    _scripts: list[Script]
    _tick_scripts: list[Script]
    _load_scripts: list[Script]

    author: str
        
    # --< Overrides >-- #
    def __init__(self, pack_name: str, namespace: str, build_path: os.PathLike, description: str = "", version: str = "1.20.1", author: str = "") -> None:
        """Represents a de-compiled datapack

        Args:
            pack_name (str): The name of the final datapack folder
            namespace (str): Namespace for datapack scripts and advancements
            build_path (os.PathLike): The target for building
            description (str, optional): Pack description. Defaults to "".
            version (str, optional): The target pack version. Defaults to "1.20.1".
        """
        self._pack_name = pack_name
        self._namespace = namespace
        self._description = description
        
        self._target_path = build_path
        self._target_version = version # This should be moved to a type class with exceptions
        
        self._dir_flags = DirectoryFlags(
            {
                "functions" : [
                    "data/minecraft/tags/functions",
                    f"{self.data_path}/functions"
                ],
                "advancements" : f"{self.data_path}/advancements",
                "tags" : f"{self.data_path}/tags",
            },
            self.full_path
        )
        
        self._script_modules = []
        self._scripts = []
        self._tick_scripts = []
        self._load_scripts =[]
        
        self.author = author
    
    
    
    # --< Methods >-- #
    def build(self) -> None:
        """Compiles the datapack to the specified build directory"""
        
        if not os.path.exists(self.build_target):
            raise DatapackException("Build path does not exist")
        
        # remove full datapack to allow for re-building
        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree(self.full_path)
        
        os.mkdir(self.full_path)
        
        # Create required directories
        self._dir_flags.create_directories()
        
        with open(os.path.join(self._target_path, self._pack_name, "pack.mcmeta"), "x") as f:
            json.dump({
                "pack": {
                    "pack_format": const._PACK_VERSION_REFERENCE[self.version],
                    "description": self._description
                }
            }, f, indent = 4)
        
        for module in self._script_modules:
            module.build()
        
        for script in self._scripts:
            script.build()
        
        # Create the tick and load files
        
        # THIS SHOUD BE A FUNCTION BECAUSE IT'S RUN TWICE
        if self._dir_flags.get_flag("functions"):
            with open(os.path.join(self.minecraft_path, "tags", "functions", "tick.json"), "x") as f:
                
                paths = []
                for script in self._tick_scripts:
                    script.build()
                    paths.append(script.relative_path)
                
                json.dump({
                    "values" : paths
                }, f, indent = 4)
            
            with open(os.path.join(self.minecraft_path, "tags", "functions", "load.json"), "x") as f:
                
                paths = []
                for script in self._load_scripts:
                    script.build()
                    paths.append(script.relative_path)
                
                json.dump({
                    "values" : paths
                }, f, indent = 4)
        
        # Creates a file for credis and other pack information
        PackFile("Credits.md", lambda : [
            "This file was created using DPCompile",
            "----------------------",
            f"Pack Name: {self._pack_name}",
            f"Author: {self.author}",
            "This pack has no registered extensions"
        ], path = "", root = self.full_path).build()
        
        
    
    def add_module(self, module: Module) -> None:
        """Adds a module to the datapack for compilation

        Args:
            module (_type_): The module to add
        """
        self._dir_flags.set_flag("functions")
        self._script_modules.append(module)
        module._root = self.full_functions_path
        module._path = ""
        module._pack = self
    
    def add_script(self, script: Script) -> None:
        """Adds a PackFile to this instance

        Args:
            file (PackFile): The file to add
        """
        self._dir_flags.set_flag("functions")
        self._scripts.append(script) # Same issue as add_dir(), change to WeakRef
        script._root = self.full_functions_path # update file's path
        script._path = ""
        script._pack = self
    
    def script(self, name: str) -> t.Callable:
        """Adds script from a function that returns a str or a list[str]

        Args:
            name (str): The name of the file

        Returns:
            t.Callable: The function that returns content
        """
        def wrapper(f: t.Callable[..., str | Command | list[str, Command]]) -> t.Callable:
            script = Script(
                name = name,
                content = f
            )
            self.add_script(script)
            return f
        return wrapper
    
    def tick(self, name: str) -> t.Callable:
        def wrapper(f: t.Callable[..., str | Command | list[str, Command]]) -> t.Callable:
            script = Script(
                name = name,
                content = f
            )
            self._dir_flags.set_flag("functions")
            self._tick_scripts.append(script)
            script._root = self.full_functions_path
            script._path = ""
            script._pack = self
            
            return f
        return wrapper
    
    def load(self, name: str) -> t.Callable:
        def wrapper(f: t.Callable[..., str | Command | list[str, Command]]) -> t.Callable:
            script = Script(
                name = name,
                content = f
            )
            self._dir_flags.set_flag("functions")
            self._load_scripts.append(script)
            script._root = self.full_functions_path
            script._path = ""
            script._pack = self
            
            return f
        return wrapper
    
    
    
    # --< Properties >-- #
    @property
    def build_target(self) -> os.PathLike:
        """The target path for compilation"""
        return self._target_path
    
    @property
    def namespace(self) -> str:
        """Datapack Namespace"""
        return self._namespace
    
    @property
    def version(self) -> str:
        """Target build version"""
        return self._target_version
    
    @property
    def full_path(self) -> os.PathLike:
        """Returns the full path to the root of the datapack, including the pack name"""
        return os.path.join(self.build_target, self._pack_name)
    
    @property
    def data_path(self) -> os.PathLike:
        """Returns the relative path to the data folder"""
        return os.path.join("data", self.namespace)
    
    @property
    def full_functions_path(self) -> os.PathLike:
        """Returns the path to the data/<namespace>/functions folder from build target"""
        return os.path.join(self.full_path, self.data_path, "functions")
    
    @property
    def minecraft_path(self) -> os.PathLike:
        return os.path.join(self.full_path, "data", "minecraft")