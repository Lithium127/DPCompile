"""
The module that holds all command classes, enabling minimal code and
checking errors at build time.
"""
from __future__ import annotations
import typing as t

from .bases import BaseCommand, Command, cmdstr

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
    
    def render(self):
        return "function", self.target_name


class Clear(BaseCommand):

    target: Selector | str
    item: str | None
    max_count: int | None

    def __init__(self, target: Selector | SelectorLiteral, item: str = None, max_count: int = None, **kwargs):
        super().__init__(**kwargs)
    
    def render(self):
        return "clear", self.target, self.item, self.max_count


class TellRaw(BaseCommand):
    """Sends a `TextElement` or `string` message to selected players"""
    
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

    def render(self):
        return "tellraw", self.target, self.content

