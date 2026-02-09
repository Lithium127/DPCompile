
from ..packfile import PackFile


class StructureFile(PackFile):
    
    def __init__(self, name):
        super().__init__(name)
    
    def render(self):
        return None