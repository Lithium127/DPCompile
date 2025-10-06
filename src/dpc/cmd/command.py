"""
The module that holds all command classes, enabling minimal code and
checking errors at build time.
"""
from __future__ import annotations
import typing as t

from .bases import BaseCommand, Command

from ..datatypes.selector import ensure_selector
from ..datatypes.textelement import TextElement

if t.TYPE_CHECKING:
    from ..datatypes.selector import Selector, SelectorLiteral



class CallFunction(BaseCommand):
    """Command that calls another function using a namespace and path"""
    
    target_name: str
    
    def __init__(self, script: t.Any, **kwargs):
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
        self.target_name = script
    
    def build(self):
        return f"function {self.target_name}"


class TellRaw(BaseCommand):
    """Sends a TextElement message to players"""
    
    target: Selector
    content: TextElement

    def __init__(self, target: Selector | SelectorLiteral, content: TextElement | str, **kwargs):
        """Sends a TextElement message to players

        Args:
            target (Selector | str): _description_
            content (TextElement | str): _description_
        """
        super().__init__(**kwargs)

        self.target = ensure_selector(target)
        self.content = TextElement(content)

    def build(self):
        return f"tellraw {self.target.to_command_str()} {self.content.to_command_str()}"

