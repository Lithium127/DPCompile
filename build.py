import os
from src.dpc import PackDSL, cmd, Module, modulemethod, Script, Blocks, Items

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
    
    # This is a file definition
    @pack.mcfn(sort="load")
    def load(script):
        """Initializes scoreboard values for this pack"""
        cmd.Log.info("Initializing scoreboards")
        cmd.TellRaw('a', f"Block information for block {Blocks.AIR}")