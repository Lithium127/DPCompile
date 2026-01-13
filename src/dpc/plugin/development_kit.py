from __future__ import annotations
import typing as t
import os

from .dpc_plugin import DPCPlugin

from ...dpc import cmd

if t.TYPE_CHECKING:
    from ..packdsl import PackDSL


class DevelopmentKit(DPCPlugin):

    tools_path: str

    def __init__(self, *, path: str = "dev_tools"):
        """Plugin that adds a number of scripts and tools to a pack
        that make development easier. Injected scripts are not 
        accessable by normal pack content and are automatically removed
        when building for production.
        """
        self.tools_path = path.rstrip("/")

    def pre_build(self, pack):
        self._add_toolkit_scripts(pack)
    

    def dev_script(self, pack: PackDSL, name: str | None = None, sort: t.Literal["tick", "load"] | None = None, path: str = None):
        """Combined shorthand to make development easier"""
        return pack.mcfn(
            name = name, 
            dev=True, 
            sort = sort, 
            path = self.tools_path + (f"/{path}" if path is not None else "")
        ) 
    
    def _add_toolkit_scripts(self, pack: PackDSL):
        
        if not pack._build_dev:
            return

        @self.dev_script(pack)
        def give_tools():
            cmd.Log("Granting player development tools")
            for tool in [
                "development stick"
            ]:
                cmd.Comment(f"Grant {tool}")
        
        @self.dev_script(pack, path="internal", sort="tick")
        def update_tool_scoreboards():
            """Scoreboards for tool activation detection go here"""
        
        @self.dev_script(pack, path="internal", sort="load")
        def dev_setup():
            """Setting up development environment, giving players development tools"""
            give_tools()

        @self.dev_script(pack, path="pack_issues")
        def attempt_reload_changes():
            cmd.Log.info(f"Reload initiated from {pack.name}.")
            cmd.Reload()
        
        @self.dev_script(pack, path="world")
        def store_local_world():
            cmd.Log.info(f"Storing area around player.")
            cmd.Comment("Do whatever to store an reload blocks here.\nProbably marker entities in the sky or something.")
