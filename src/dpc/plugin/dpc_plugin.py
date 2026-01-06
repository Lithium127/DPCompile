from __future__ import annotations
from abc import ABC, abstractmethod
import typing as t

if t.TYPE_CHECKING:
    from ..IO.packfile import PackFile
    from ..packdsl import PackDSL


class DPCPluginError(Exception):
    pass

class DPCPlugin(ABC):
    """The base class for all plugins, defines a number
    of hooks that are run with set data.
    
    Available Hooks:
        `pre_build()`
        `post_build()`
        `render_file()`
        `on_build_error()`
        `on_def_error()`
    
    """

    def pre_build(self, pack: 'PackDSL') -> None:
        """Runs before the pack context is entered, meaning
        no content except for the base pack config and data
        from other plugins is added to the pack.

        Args:
            pack (PackDSL): The pack this plugin is registered to
        """
    
    def post_build(self, pack: 'PackDSL') -> None:
        """Runs when the pack context exits, after all
        resources have been added to the build directory.

        Args:
            pack (PackDSL): The pack this plugin is registered to
        """

    def render_file(self, pack: PackDSL, file: PackFile, path: str) -> None:
        """A hook for rendering a file, called after
        a file has finished rendering but before the
        file is added to the directory.

        If multiple plugins use this method, the hooks
        are called in the order that the plugins are
        added to the pack.

        Args:
            pack (PackDSL): The pack this plugin is registered to
            file (PackFile): The rendered pack file
        """
    
    def on_build_error(self, pack: PackDSL, exc: Exception) -> None:
        """A hook that runs when a pack encounters an
        exception during the building process.

        Args:
            pack (PackDSL): The pack that this plugin is registered to
            exc (Exception): The exception thrown
        """
    
    def on_def_error(self, pack: PackDSL, exc: Exception) -> None:
        """A hook that runs when a pack encounter an
        exception in the definition process.

        Args:
            pack (PackDSL): The pack that this plugin is registered to
            exc (Exception): The exception thrown
        """


class PluginCollection(list[DPCPlugin]):
    """A list of plugins"""

    def call_plugins(self, hook_name: str, *args, **kwargs) -> None:
        """Calls the hook with a given name from all
        registered plugins within this collection.

        Args:
            hook_name (str): The name of the plugin hook to run, see `DPCPlugin` for possible hooks

        Raises:
            DPCPluginError: If there was an error within a hook call
        """
        for plugin in self:
            try:
                plugin.__getattribute__(hook_name)(*args, **kwargs)
            except Exception as e:
                raise DPCPluginError(f"Error running plugin hook '{hook_name}' with plugin {plugin.__class__.__name__}") from e