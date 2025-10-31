import os
from src.dpc import PackDSL, cmd, Blocks

LOCAL_BUILD_PATH = os.environ.get("LOCAL_BUILD_PATH")
WORLD_BUILD_PATH = os.environ.get("WORLD_BUILD_PATH")

# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.4",
        LOCAL_BUILD_PATH
    ).build_dev() as pack:

    # This is a file definition
    @pack.mcfn(sort="load")
    def load(script):
        """Initializes scoreboard values for this pack"""
        cmd.Log.info("Pack Loaded!")
    
    for block in Blocks:
        pack.mcfn(f"{block.name}_info", path="blocks")(
            lambda: cmd.TellRaw("s", f"Info for {block.display_name}. Source: {block.namespace}, Name: {block.name}, Hardness: {block.hardness}")
        )