

from ..scripts import Module
from .. import command as cmd
from ..entities import Entity

class DPItem(Module):
    
    def __init__(self, item_name: str, pack: object) -> None:
        super().__init__(item_name, pack)
        
        @self.script("give")
        def give() -> list[str]:
            return [
                cmd.Execute().as_(Entity.selector("@s")).at(Entity.selector("@s"))
            ]
        
        