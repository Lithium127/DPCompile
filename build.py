import os
from src.dpc import PackDSL, cmd, Module, modulemethod, Script, Blocks

from src.dpc.datatypes.enum.item_enum import Items

LOCAL_BUILD_PATH = os.environ.get("LOCAL_BUILD_PATH")
WORLD_BUILD_PATH = os.environ.get("WORLD_BUILD_PATH")

# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.4",
        LOCAL_BUILD_PATH,
        dev = True
    ) as pack:

    @pack.mcfn(sort="load")
    def load():
        cmd.Comment(cmd.Log(f"Pack Loaded!, running startup script {initialize()}"))
    
    @pack.mcfn()
    def initialize(script):
        """Performs required startup for all groups"""
        cmd.Log(f"Running initialization...").dev()