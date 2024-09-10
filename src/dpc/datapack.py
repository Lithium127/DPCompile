import os
import typing as t

import contextlib
import shutil

from .exception import DatapackException

# Path.mkdir(full_path, parents=True, exist_ok=True) 

class Datapack:
    """Represents a de-compiled datapack"""
    _pack_name: str
    _namespace: str
    
    _description: str
    
    _target_path: os.PathLike
    _target_version: str
    
    # --< Overrides >-- #
    def __init__(self, pack_name: str, namespace: str, build_path: os.PathLike, description: str = "", version: str = "1.20.1") -> None:
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
    
    
    
    # --< Methods >-- #
    def build(self) -> None:
        """Compiles the datapack to the specified build directory"""
        
        if not os.path.exists(self.build_target):
            raise DatapackException("Build path does not exist")
        
        # remove full datapack to allow for re-building
        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree(self.full_path)
        
        os.mkdir(self.full_path)
        
        
    
    def add_module(self, module) -> None:
        """Adds a module to the datapack for compilation

        Args:
            module (_type_): The module to add

        Raises:
            NotImplementedError: Uhhh...
        """
        raise NotImplementedError()
    
    
    
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
        return os.path.join(self.build_target, self._pack_name)
    