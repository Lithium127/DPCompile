from __future__ import annotations
import typing as t
import os

from .pack import PackBase, PackContext, PackBuildError
from .IO.script import Script, ScriptDecoratable, ScriptError
from .IO.tagtable import TagTable

if t.TYPE_CHECKING:
    from .namespace import Namespace
    from .IO.packfile import PackFile



class DatapackContext(PackContext, ScriptDecoratable):
    
    def add_file(self, file, path = None):
        return self.pack.add_file(file, path or "/")
    
    def add_script_to_taglist(self, script: Script, on_tick: bool = False, on_load: bool = False):
        files: list[PackFile] = self.pack._directory.get_files("data/minecraft/tags/function")

        for sort, required in [("tick", on_tick), ("load", on_load)]:
            if not required: continue

            if files is not None:
                for file in files:
                    if file.name == sort and isinstance(file, TagTable):
                        file._entries.append(script)
            else:
                # Otherwise create the folder of given type
                self.add_tag_table(
                    TagTable('function', sort, [script], namespace="minecraft")
                )
    
    def add_tag_table(self, table: TagTable) -> None:
        table.set_pack_parent(self)
        self.add_file(
            table,
            f"data/{table.namespace}/tags/{table.sort}"
        )

    @property
    def _pack_reference(self):
        return self.pack
    
    @property
    def _file_root(self):
        return os.path.join(self.pack.build_dir, self.pack._pack_name)



class Datapack(PackBase):

    _PACK_CONTEXT_TYPE = DatapackContext

    def __init__(self, name, nmsp, build_dir, version = ...):
        super().__init__(name, nmsp, build_dir, version)

    def __enter__(self) -> DatapackContext:
        return super().__enter__()

    def _prerender_scripts(self) -> None:
        try:
            for path, file in self._directory.files():
                if isinstance(file, Script):
                    file.render()
        except ScriptError as e:
            raise PackBuildError(e.script, f"Exception found within {self._pack_name} " + 
                            f"building for version {self.version} [{self.version.pack_reference}] " +
                            f"while rendering '{e.script.full_name}' ({e.script.namespace_name})") from e


    def _populate_files(self):
        self._prerender_scripts()
        super()._populate_files()
