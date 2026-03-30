from __future__ import annotations
import typing as t

import os
import shutil

from collections import defaultdict

from .namespace import Namespace
from .plugins.dpc_plugin import PluginCollection, DPCPlugin

from .mctypes.version import Version

from .IO.packfile import PackFile


class PackError(Exception):
    """Exception in a given pack"""
    pack: PackBase

    def __init__(self, pack: PackBase, *args):
        super().__init__(f"Exception occurred in Pack {self.pack} (namespace: {self.pack.namespace})\n", *args)
        self.pack = pack

class PackBuildError(PackError):
    
    file: PackFile

    def __init__(self, file: PackFile, *args):
        self.file = file
        super().__init__(*args)

class PackDirectory:
    
    # TODO: Make tree reference a 'Buildable' or 'Renderable' interface for modules
    tree: dict[str, list[PackFile]]
    
    def __init__(self):
        self.tree = defaultdict(list)
    
    def register(self, path: str, item: PackFile) -> None:
        if " " in path:
            raise PackError(f"Invalid path for '{type(item)}'. Requested path '{path}' includes invalid characters.")
        self.tree[path].append(item)
    
    def get_files(self, path: str) -> list[PackFile] | None:
        """Returns the list of files at a given path
        within this directory

        Args:
            path (str): The path to fileset

        Returns:
            list[PackFile]: The list of files at the given path
        """
        return self.tree.get(path, [])
    
    def files(self) -> t.Generator[tuple[str, PackFile]]:
        for path in self.tree.keys():
            for file in path:
                yield (path, file)



class PackContext:
    """An open pack context, which acts as
    an abstraction of the pack context and 
    directory"""

    _tied_pack: PackBase
    
    def __init__(self, pack: PackBase):
        """Creates a given pack context from a pack `pack`

        Args:
            pack (PackBase): The pack this context wraps
        """
        self._tied_pack = pack

    def setup(self) -> None:
        """Performs setup operations for this context"""
        pass

    def cleanup(self) -> None:
        """Performs cleanup operations for this context"""
        pass

    @property
    def pack(self) -> PackBase:
        """The pack this context exists in"""
        return self._tied_pack
    
    @property
    def namespace(self) -> PackBase:
        """The namespace for the pack this context exists in"""
        return self.pack.namespace


class BuildFlag:

    _FLAG_DEV  = 0
    _FLAG_PROD = 1

    _flag: int

    def __init__(self, flag: int = 0, /):
        self._flag = flag
    
    def __eq__(self, value):
        if not isinstance(value, BuildFlag):
            return False
        
        return self._flag == value._flag

    @property
    def is_dev(self) -> bool:
        return self._flag == self._FLAG_DEV
    
    @property
    def is_prod(self) -> bool:
        return self._flag == self._FLAG_PROD



class PackBase:
    """The base for a compilable package. Packs contain a
    directory that can be zipped, and exist within a namespace
    that enables simple querying of space contents.

    Packs have capabilities defined at initialization and helper
    methods and decorators for simple production of internal
    files.
    """

    _namespace: Namespace
    _pack_name: str

    _build_dir: str
    _build_flag: BuildFlag
    
    _directory: PackDirectory
    _plugins: PluginCollection

    _version: Version

    _context: PackContext

    _PACK_CONTEXT_TYPE: t.Type[PackContext] = PackContext
    """The type that context should be derived from"""

    def __init__(self, name: str, nmsp: Namespace | str, build_dir: str, version: Version = None):
        
        if not isinstance(nmsp, Namespace):
            nmsp = Namespace(nmsp)
        self._namespace = nmsp
        self._pack_name = name

        self._directory = PackDirectory()
        self._plugins = PluginCollection()

        if not (isinstance(version, str) or isinstance(version, Version)):
            self._version = Version.maximum()
        else: 
            self._version = version if isinstance(version, Version) else Version(version)

        self._build_dir = build_dir
        self._build_flag = BuildFlag()

        self._context = None
    
    
    def __enter__(self):
        if self._context is None:
            context = self._obtain_safe_context_type()
            self._context = context

        self._context.setup()

        return self._context

    def __exit__(self, exc_type, exc, tb):
        
        # Context closing methods
        self._context.cleanup()

        if exc:
            # For user caused errors within pack scope
            # emit error without building
            self._plugins.call_plugins("on_def_error", self, exc)
            return False

        self.build()

    def __str__(self) -> str:
        return f"{object.__str__(self)}"


    def _obtain_safe_context_type(self) -> PackContext:
        """Produces a safe context type for opening a pack subclass
        context. This context will be instanced and returned as an
        instance.

        Raises:
            PackError: If the context available is not safe

        Returns:
            PackContext: The context opened with this pack
        """
        if not issubclass(self.__class__._PACK_CONTEXT_TYPE, PackContext):
            raise PackError(self, "Could not produce safe context for pack assembly.")
        
        
        return self.__class__._PACK_CONTEXT_TYPE(self)


    def _add_file(self, o: PackFile, fp: str, /) -> None:
        """Adds a file to this pack's internal directory. It is up to the
        pack to determine what methods are used for adding files. Files are
        validated to make sure they are permitted within a pack of this type

        Args:
            o (PackFile): The PackFile object to add at the given location
            fp (str): The path to this resource relative to pack root
        
        Raises:
            PackError: If the provided file is not permitted in a pack of this type
        """
        # Validate that this given file is of the correct type
        if not self._file_permitted(o):
            raise PackError(f"Attempted to add file type that is prohibited by pack {self} of type {type(self)}. File type {type(o)} rejected at path f{fp}.")
        o.set_pack_parent(self) # Need better method for shared files
        self._directory.register(fp, o)
    

    def add_file(self, file: PackFile, path: str, /) -> None:
        return self._add_file(file, path)
    

    def _add_plugin(self, target: DPCPlugin, /) -> None:
        """Internal addition of plugins to this pack. Calls the register
        hook after addition to targets.

        Args:
            target (DPCPlugin): The plugin instance to add to this pack

        Raises:
            PackError: If the targeted instance is not of type DPCPlugin
        """
        if not isinstance(target, DPCPlugin):
            raise PackError(f"Cannot append non DPCPlugin type to pack plugin list. Attempted with type {type(target)}")
        self._plugins.append(target)
        target.on_register(self, len(self.plugins) - 1)    


    def build(self) -> None:
        """Performs this build operation for this pack.

        Raises:
            e: Any errors generated within the build process
        """
        self._plugins.call_plugins("pre_build", self)
        try:
            Version._CURRENT_VERSION = self.version
            self._populate_files()
        except Exception as e:
            self._plugins.call_plugins("on_build_error", self, e)
            # if self._error_behavior == "strict":
            raise e
            # else:
            #     # Print Error to console and continue
            #     print(f"{type(e).__name__} error occurred in PackDSL building for version {self.version}. Error handling set to '{self._error_behavior}', continuing with build for next version.")
        finally:
            Version._CURRENT_VERSION = None
        self._plugins.call_plugins("post_build", self)


    def _clear_target_directory(self) -> bool:
        """Clears the derectory noted as the build target
        for this pack.

        This should attempt to identify if the target directory is
        populated with a primary folder matching the directory
        that this pack would build in, or if the folder is already
        empty, otherwise this should fail and not touch anything.

        Returns:
            bool: If the target directory was able to be cleared.
        """
        if os.path.exists(self._build_dir):
            shutil.rmtree(self._build_dir, ignore_errors=True)
        os.makedirs(self._build_dir, exist_ok=True)


    def _populate_files(self) -> None:
        """Populates this pack's build directory with files that
        were added to this pack.

        Raises:
            PackError: If the build directory was unable to be cleared
        """
        
        if not self._clear_target_directory():
            raise PackError(self, f"Unable to clear files from target directory '{self._build_dir}'.")
        
        for path in self._directory.tree.keys():
            # Join relative paths to build path
            abs_path = os.path.join(self._file_root, path) if path != "/" else self._file_root

            renderable_files = []
            for file in self._directory.get_files(path):
                if file.rendering_allowed(self):
                    renderable_files.append(file)
            
            if len(renderable_files) <= 0:
                continue # Do not create empty directories

            os.makedirs(abs_path, exist_ok=True)

            for file in renderable_files:
                file.write(path) # Files manage their own rendering

                # Issue with errors in rendering means that files should likely pre-render and cache their contents unless unable to
                
                self._plugins.call_plugins("render_file", self, file, path)


    def _file_permitted(self, file: PackFile) -> bool:
        """Validates that a file of this type is permitted within this pack

        Args:
            file (PackFile): The file to validate

        Returns:
            bool: If this file is permitted
        """

        if not isinstance(file, PackFile):
            return False

        return True


    @property
    def _has_context(self) -> bool:
        return (self._active_context is not None)


    @property
    def namespace(self) -> Namespace:
        return self._namespace


    @property
    def plugins(self) -> PluginCollection:
        return self._plugins


    @property
    def version(self) -> Version:
        return self._version