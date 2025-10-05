"""
The module that holds all command classes, enabling minimal code and
checking errors at build time.
"""
from __future__ import annotations
import typing as t

from .bases import BaseCommand


class Command(BaseCommand):
    """A literal command without structure, appending
    its content directly to a script."""
    
    content: str
    
    def __init__(self, content: str, **kwargs):
        """A literal command without structure, returns
        the base string passed to the command when built.

        This class exists for implementing custom commands
        or literals that should be appended to the resulting
        file without the need for excessive classes.
        
        ```python
        cmd = Command("This is a test command")
        cmd.build() # > str('This is a test command')
        ```

        Args:
            content (str): The content of the command
        """
        super().__init__(**kwargs)
        self.content = content
    
    def build(self):
        return self.content

class Comment(BaseCommand):
    """A comment within a script, for developer notes"""
    
    content: str
    
    def __init__(self, content: str, **kwargs):
        super().__init__(**kwargs)
        self.content = content
    
    def build(self):
        if "\n" in self.content:
            return "\n".join([f"# {line}" for line in self.content.split("\n")])
        return f"# {self.content}"




class CallFunction(BaseCommand):
    """Command that calls another function using a namespace and path"""
    
    target_name: str
    
    def __init__(self, target_name: str, **kwargs):
        """Creates a call to a function with the given
        name. Names must consist of a namespace and a
        path to the function that includes the name of
        the function.
        
        example: `namespace:path/to/function` or 
        `tcev:raycasts/run_at_block`

        Args:
            target_name (str): _description_
        """
        super().__init__(**kwargs)
        self.target_name = target_name
    
    def build(self):
        return f"function {self.target_name}"


class TellRaw(BaseCommand):
    pass


