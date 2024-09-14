import os
import typing as t

from pathlib import Path


class DirectoryFlags(object):
    """Creates required directories conditionally based on modules added"""
    
    _flags: dict[str, os.PathLike]
    _root_path: os.PathLike
    
    def __init__(self, flags: dict[str, os.PathLike | list[os.PathLike]], root_path: os.PathLike) -> None:
        """Creates a set of paths based on conditional flags for each path

        Args:
            flags (dict[str, os.PathLike  |  list[os.PathLike]]): The set of paths and keys to reference their flags
            root_path (os.PathLike): The target build path
        """
        self._root_path = root_path
        
        self._flags = {}
        for key, value in flags.items():
            self._flags[key] = {
                "path" : value,
                "set" : False
            }
    
    def set_flag(self, flag: str, *, value: bool = True) -> None:
        """Sets a directories flag

        Args:
            flag (str): The key to the directory
            value (bool, optional): Value to set flag to. Defaults to True.
        """
        self._flags[flag]["set"] = value
    
    def get_flag(self, flag: str) -> bool:
        return self._flags[flag]["set"]

    
    def create_directories(self) -> None:
        """Creates paths that have their flag set to True"""
        for path in self._flags.values():
            if path["set"]:
                if isinstance(path["path"], list):
                    [Path.mkdir(Path(os.path.join(self._root_path, pth)), parents=True, exist_ok=True) for pth in path["path"]]
                else:
                    Path.mkdir(os.path.join(self._root_path, path["path"]), parents=True, exist_ok=True)


class PackDirectory(object):
    """Represents a directory within the datapack folder"""
    
    _path: os.PathLike | None
    _root: os.PathLike | None
    _name: str
    
    _directories: list['PackDirectory']
    _files: list['PackFile']
    
    _pack: object
    
    def __init__(self, name: str, *, path: os.PathLike | None = None) -> None:
        self._name = name
        self._path = path
        self._root = None
        
        self._directories = []
        self._files = []
    
    def build(self) -> None:
        """Builds this directory and all sub-dirs"""
        os.mkdir(self.path)
        for file in self._files:
            file.build()
    
    def add_dir(self, dir: 'PackDirectory') -> None:
        """Adds a subdirectory to this instance

        Args:
            dir (PackDirectory): The directory to add
        """
        self._directories.append(dir) # consider changing to a WeakRef to the directory
        dir._root = self._root
        dir._path = self.relative_path # update path
        dir._pack = self._pack
    
    def add_file(self, file: 'PackFile') -> None:
        """Adds a PackFile to this instance

        Args:
            file (PackFile): The file to add
        """
        self._files.append(file) # Same issue as add_dir(), change to WeakRef
        file._root = self._root
        file._path = os.path.join(self._path, self._name) # update file's path
        file._pack = self._pack
    
    @property
    def name(self) -> str:
        """The name of the this directory"""
        return self._name
    
    @property
    def path(self) -> os.PathLike:
        """The path to this directory relative to root"""
        return os.path.join(self._root, self._path, self.name)
    
    @property
    def relative_path(self) -> os.PathLike:
        """Return the path to this file relative to the datapack"""
        return f"{self._pack.namespace}:{os.path.join(self._path, self.name)}"
    

class PackFile(object):
    
    _DEFAULT_SUFFIX: str = "txt"
    
    _path: os.PathLike | None
    _root: os.PathLike | None
    _name: str
    _suffix: str
    
    _content: t.Callable
    _pack: object # Datapack
    
    def __init__(self, name: str, content: str | t.Callable[..., str | list[str]], *, path: os.PathLike | None = None, root: os.PathLike | None = None) -> None:
        """Represents a file within this pack

        Args:
            name (str): The name of the file
            content (str | t.Callable): A function that returns the content of the file
            path (os.PathLike | None, optional): The requested path to the file, used only for decorators. Defaults to None.
        """
        name = name.split(".")
        self._name = name[0]
        try:
            self._suffix = name[1]
        except IndexError:
            self._suffix = self._DEFAULT_SUFFIX
        self._path = root
        self._root = root
        self._content = content
    
    def build(self) -> None:
        """Creates this file in the targeted directory and populates with content"""
        with open(self.path, "x") as f:
            content = self._content()
            if isinstance(content, list):
                content = "\n".join(content)
            try:
                f.write(f"# This file was automatically generated for {self._pack._pack_name}\n{content}")
            except AttributeError:
                f.write(f"{content}")
    
    @property
    def name(self) -> str:
        """The name of this file"""
        return f"{self._name}.{self._suffix}"
    
    @property
    def path(self) -> os.PathLike:
        """The path to this file relative to the root path"""
        return os.path.join(self._root, self._path, self.name)
    
    @property
    def relative_path(self) -> os.PathLike:
        return f"{self._pack.namespace}:{os.path.join(self._path, self._name)}"