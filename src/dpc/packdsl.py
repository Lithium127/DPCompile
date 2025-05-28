from __future__ import annotations
import typing as t
import os
import shutil

from enum import Enum
from collections import defaultdict

from .IO.mcmeta import McMeta
from .IO.script import Script, ScriptDecoratable, ScriptError
from .IO.tagtable import TagTable
from .datatypes import Version

from .command import Comment
from .datatypes import Scoreboard

if t.TYPE_CHECKING:
    from .IO.packfile import PackFile



class PackError(Exception):
    pass


class PackFileSystem:
    
    # TODO: Make tree reference a 'Buildable' or 'Renderable' interface for modules
    tree: dict[str, list[PackFile]]
    
    def __init__(self):
        self.tree = defaultdict(list)
    
    def register(self, path: str, item: PackFile) -> None:
        self.tree[path].append(item)
    
    def get_files(self, path: str) -> list[PackFile] | None:
        """Returns the list of files at a given path
        within this directory

        Args:
            path (str): The path to fileset

        Returns:
            list[PackFile]: The list of files at the given path
        """
        return self.tree.get(path, None)


class PackDSL(ScriptDecoratable):
    """Represents a datapack, holding context and alternate data.
    
    When using PackDSL as a context with the `with` statement the `build()` method is called
    implicitly during the exit step unless configuration requests a differed build step. The
    instance will build for all given versions, applying patches and hacks to avoid 
    pack behavior inconsistancies across different versions.
    
    Plugins are registered on context entry and exposed to files and assets as required.
    
    Basic Usage:
    ```python
    with PackDSL(...) as pack:
        # Pack data generated
        ...
    ```
    """
    
    _pack_name: str
    _namespace: str
    _version: Version # TODO: Replace versioning with a list of buildable versions. Add a property for the current version determined through context
    _plugins: list
    _meta: McMeta
    
    build_dir: str
    _build_dev: bool
    
    directory: PackFileSystem
    
    _scoreboards: set[Scoreboard]
    
    def __init__(self, 
                 pack_name: str,
                 namesapce: str,
                 description: str,
                 version: Version | str | list[int] | tuple[int, int, int],
                 out_dir: str, # TODO: Automatic directory loading to same location or to game.
                 *,
                 dev: bool = True,
                 plugins: list | None = None):
        """Represents a full datapack context that loads functions and compiles to set versions.
        
        #### Example Usage
        ```python
        with PackDSL(<namespace>, <desc>, <version>) as pack:
            ...
        
        # Or with builders
        with PackDSL(
            <namespace>, <desc>, <version>
        ).with_build_type(
            PackDSL.OPTIONS.BUILD_DEV
        ) as pack:
            ...
        ```
        
        This object is intended to be used in a `with PackDSL(...) as pack` statement that preceeds
        all function construction and module registration. The `build()` method is called implicitly
        at context exit and builds for all given versions, and for the set type.
        
        The pack context will attempt to build the given set of scripts and modules for all versions
        that are given to it, applying a pre-set list of patches and hacks to enable features in
        earlier versions of the game.
        
        There are a number of builder methods that modify the behavior of the build call or script
        registration.
        
        `with_build_type(PackDSL.OPTIONS.BUILD_*)`, a method that sets the type of build this instance
        will perform at context exit.
        
        `with_plugins(*<plugins>)`, a method that enables plugins that are passed to it. These plugins
        are added to the context and register hooks at build call.

        Args:
            namesapce (str): The namespace for this datapack, required to link any files or scripts to this instance
            version (tuple[int, int, int], optional): The version this pack should build in. Defaults to (0, 0, 0).
            out_dir (str, optional): The absolute path for the final directory of this instance. Defaults to "".
            plugins (list | None, optional): A list of plugins to use in development. Defaults to None.
        """
        super().__init__()
        self._pack_name = pack_name
        self._namespace = namesapce
        # Create metadata
        self.directory = PackFileSystem()
        
        self._meta = McMeta(description=description)
        self.register_file("/", self._meta)
        
        self._version = version if isinstance(version, Version) else Version(version)
        self._plugins = plugins or []
        
        self.build_dir = out_dir
        # Default building for development
        self._build_dev = dev
        
        # Scoreboard registry
        self._scoreboards = set()
    
    
    
    def __enter__(self) -> PackDSL:
        # TODO: Add plugin initialization
        
        return self
    
    
    
    def __exit__(self, exc_type, exc, tb) -> bool | None:
        if exc:
            # For user caused errors within pack scope
            # emit error without building
            return False
        self._build()
    
    
    
    # TODO: Replace this call with a multiple dispatch for either single version building
    # or multiple versioning, creating a group folder to contain each versioned pack within.
    
    # Example:
    # Single build - C:/.../<pack name>/<namespace>/...
    # Multiple build - C:/.../<pack name> builds/<pack name> <version>/<namespace>/...
    def _build(self) -> None:
        """Performs the action of compiling this pack.
        This function is automatically run when a pack
        context ends, and ensures that required contexts
        are set properly."""
        # TODO: Register plugin hooks
        
        if os.path.exists(self._file_root):
            shutil.rmtree(self._file_root, ignore_errors=True)
        os.makedirs(self._file_root, exist_ok=True)
        
        try:
            self._prerender_scripts()
        except ScriptError as e:
            raise PackError(f"Exception found within {self._pack_name} " + 
                            f"building for version {self.version} [{self.version.pack_reference}] " +
                            f"while rendering '{e.script.full_name}' ({e.script.namespace_name})") from e
        self._build_scoreboard_initializer()
        
        for path in self.directory.tree.keys():
            # Move from relative paths to absolute
            abs_path = os.path.join(self._file_root, path) if path != "/" else self._file_root
            
            # Create list of files that are allowed to be rendered
            files = []
            for file in self.directory.tree[path]:
                if self._build_dev or (not file._is_dev):
                    files.append(file)
            # Do not make directory if there are no files in it
            if len(files) < 1:
                continue
            
            # Build parent directory
            os.makedirs(abs_path, exist_ok=True)
            
            for file in files:
                file.write(path)
                # Development logging of file content to console
                print(f"\n[{file.full_name}]{(' : Script' + (' instance passed' if file._pass_self else '')) if isinstance(file, Script) else ''}")
                print(f"  @ <{path}>")
                print("\n".join([f"  |  {line}" for line in file.render().split("\n")]))
    
    
    def with_plugins(self, plugins: list) -> PackDSL:
        """Sets list of plugins to use with 

        Args:
            plugins (list): _description_

        Returns:
            PackDSL: _description_
        """
        return self
    
    
    def add_script_to_taglist(self, script: Script, sort: t.Literal["tick", "load"] = "tick"):
        files: list[PackFile] = self.directory.get_files("data/minecraft/tags/function")
        if files is not None:
            for file in files:
                if file.name == sort and isinstance(file, TagTable):
                    file._entries.append(script)
                    return
        # Otherwise create the folder of given type
        self.add_tag_table(
            TagTable('function', sort, [script], namespace="minecraft")
        )
    
    
    def add_tag_table(self, table: TagTable) -> None:
        table.set_pack_parent(self)
        self.register_file(
            f"data/{table.namespace}/tags/{table.sort}",
            table
        )
    
    
    def register_file(self, path: str, file: PackFile) -> None:
        """Registers a file with this packs internal directory,
        attaching the pack as the parent of the file for rendering

        Args:
            path (str): The path to the file location relative to the pack root
            file (PackFile): The file to add
        """
        file.set_pack_parent(self)
        self.directory.register(path, file)
    
    
    def register_scoreboard(self, scoreboard: Scoreboard) -> None:
        """Registers a given scoreboard to be initialized
        in an independent load script. This function is run
        automatically whenever a command that modifies the
        value or attribute of a scoreboard is built within a
        script context.

        Args:
            scoreboard (Scoreboard): The scoreboard to register
        """
        self._scoreboards.add(scoreboard)
    
    
    def _build_scoreboard_initializer(self) -> None:
        """Adds a script to the set of loading scripts
        that will initialize all used scoreboards referenced
        by this pack.
        """
        if len(self._scoreboards) < 1:
            return None
        # The problem is that scoreboards will only be acknowledged after
        # the script is run, which only happens at build time.
        def initialize_scoreboards():
            """Auto-generated function that initializes all required scoreboards"""
            Scoreboard.initialize_scoreboards()
        
        self.add_script(
            Script("initialize_scoreboards", initialize_scoreboards),
            ticking=False
        )
        
        
    @property
    def version(self) -> Version:
        return self._version
    
    
    @property
    def meta(self) -> McMeta:
        """Returns this pack's internal metadata"""
        return self._meta
    
    
    @property
    def _file_root(self) -> str:
        return os.path.join(self.build_dir, self._pack_name)
    
    
    @property
    def _pack_reference(self) -> PackDSL:
        return self