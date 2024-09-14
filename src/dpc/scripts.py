import os
import typing as t

from .shared import PackFile, PackDirectory
from .command import Command

class Script(PackFile):
    
    _DEFAULT_SUFFIX = "mcfunction"
    
    _content: str | Command | list[str, Command]
    
    def __init__(self, name: str, content: t.Callable[..., str | Command | list[str, Command]], *args, **kwargs) -> None:
        """Represents a script.mcfunction for a datapack

        Args:
            name (str): The name of the script
            content (t.Callable): A function that returns the content of the script
        """
        super(Script, self).__init__(name, content, *args, **kwargs)
    
    def build(self) -> None:
        aspect = "x" if not os.path.exists(self.path) else "a"
        
        with open(self.path, aspect) as f:
            content = self._content()
            if not isinstance(content, list):
                content = content.split("\n")
            
            for index, line in enumerate(content):
                if isinstance(line, Command):
                    line.update_data(index, self)
                    content[index] = line.construct()
            
            content = "\n".join(content)
            
            f.write(f"{'# This file was automatically generated for ' + self._pack._pack_name if aspect == 'x' else ''}\n{content}")

class Module(PackDirectory):
    
    def __init__(self, name: str, pack: object) -> None:
        super().__init__(name)
        pack.add_module(self)
        if isinstance(pack, self.__class__):
            self._root = pack._root
        else:
            self._root = pack.full_functions_path
    
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
            self.add_file(script)
            return f
    
        return wrapper
    
    def add_module(self, module) -> None:
        self.add_dir(module)