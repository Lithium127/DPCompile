from __future__ import annotations
import typing as t
import os

from abc import ABC, ABCMeta, abstractmethod

if t.TYPE_CHECKING:
    from ..packdsl import PackDSL

class FileParentable(metaclass=ABCMeta):
    """An abstract interface to give a class the required properties to parent packfiles
    
    Requires that the class overrides the `file_root` property to return the absolute path
    within the file system that the paths of all child files will be relative to.
    
    ```python
    class Module(FileParentable):
        # Other code
        ...
        
        @property
        def file_root(self) -> str:
            # Implementation to find absolute path
            return ...
            
    ```
    """
    
    # TODO: Depricate collectors, use directory from packdsl
    _collectors: list[PackFile] = []
    """The list of files this instance is parent to"""
    
    def add_file(self, file: PackFile) -> None:
        """Adds a given file to this instance.

        Args:
            file (PackFile): The file to add
        """
        self._collectors.append(file)
    
    @property
    @abstractmethod
    def _pack_reference(self) -> PackDSL:
        """Returns the required reference to a pack to enable decoration

        Returns:
            PackDSL: The reference to the parent pack
        """
        pass
    
    @property
    @abstractmethod
    def _file_root(self) -> str:
        """Returns the absolute location where files that are parented
        by this object should begin their relative paths.

        Returns:
            str: The absolute path this object manages
        """
        pass


class PackFile(ABC):
    """Represents a file that can save rendered content to a pack directory.
    
    Alone this class will not do anything of note. Subclasses bust override the `render()` method
    to generate content within the file. If `render()` return `None` then no file is created
    and the process continues.
    
    ```python
    # Simplest case by which a file can be rendered
    with PackDSL(...) as pack:
        file = PackFile(pack, "test.txt")
        file.write() # Unmanaged write call, attach file to pack or module
    ```
    """
    
    _p: PackDSL
    _is_dev: bool
    extension: str
    name: str
    path: str
    
    def __init__(self, name: str) -> None:
        # TODO: Passing the pack as a reference at init time is not needed as files need to be attached to the pack
        # anyway in order for the file to build properly.
        """Creates a representation of a file contained within a pack directory.

        ```python
        with PackDSL(out_dir="/path/to/build/dir") as pack:
            PackFile(pack, "relative/path/to/file.txt")
        ```
        
        Args:
            pack (PackDSL): The parent pack or module, attributes from this
                            parent will be pulled to determine the location
                            this file should be created at, all parents
                            require a `build_dir` attribute that holds a
                            relative path.
            rel_path (str): The slash seperated relative path to this file, the 
                            filename is pulled from the end of this list. If this
                            file is added to a pack or module then the path will
                            be relative to the location that module points to.
        """
        self._p = None
        
        # Format and pull path and name
        self.full_name = name
        self._is_dev = False
        
        
    
    def write(self, path: str | None = None) -> None:
        """Writes this file to the pack via the given directory"""
        use_path = path or self.path
        full = os.path.join(self.pack._file_root, use_path) if use_path != "/" else self.pack._file_root
        os.makedirs(os.path.dirname(full), exist_ok=True)
        content = self.render()
        # Only write file if content exists
        if content is not None:
            with open(f"{full}/{self.full_name}", "w", encoding="utf-8") as f:
                f.write(content)
    
    
    
    @abstractmethod
    def render(self) -> str | None:
        """Function that generates content for this file.
        
        This function must return a single string that will
        be written to the file. Each file is required to
        interpret its own content and organize that into
        data into a writable string, including `'\\n'` characters
        as required for formatting.

        Returns:
            str(None) : The content within this file. If `None` then file will not be created.
        """
        return None
    
    
    
    def set_pack_parent(self, pack: PackDSL) -> None:
        """Sets a given pack as the parent for this
        packfile.

        Args:
            pack (PackDSL): The pack that parents this file
        """
        self._p = pack
    
    
    
    @property
    def pack(self) -> PackDSL:
        """A reference to the pack that parents this file. 
        This attribute is only set when the file is attached 
        to a pack for automatic rendering"""
        return self._p
    
    
    
    @property
    def has_pack(self) -> bool:
        """Wether or not this file is attached to a pack."""
        return self._p is not None
    
    
    
    @property
    def full_name(self) -> str:
        return f"{self.name}.{self.extension}"
    
    
    
    @full_name.setter
    def full_name(self, value: str) -> None:
        value = value.split(".")
        self.name = value[0]
        self.extension = value[1] if len(value) > 1 else None
    