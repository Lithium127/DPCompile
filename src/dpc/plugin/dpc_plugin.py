from abc import ABC, abstractmethod
import typing as t

if t.TYPE_CHECKING:
    from ..IO.packfile import PackFile
    from ..packdsl import PackDSL


class DPCPlugin(ABC):
    """The base class for all plugins, defines a number
    of hooks that are run with set data.
    
    Available Hooks:
        `pre_build()`
        `post_build()`
        `render_file()`
        `post_render()`
    
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

    def render_file(self, pack: 'PackDSL', file: 'PackFile', path: str) -> None:
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
    


class PluginCollection(list):
    """A list of plugins"""

    def call_plugins(self, hook_name: str, *args, **kwargs) -> None:
        """Calls a given function with all plugins as
        the first argument.

        Args:
            meth (callable): The method 
        """
        for plugin in self:
            try:
                plugin.__getattribute__(hook_name)(*args, **kwargs)
            except Exception as e:
                raise e