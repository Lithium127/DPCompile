import os
from src.dpc import PackDSL, cmd, Blocks, Items

LOCAL_BUILD_PATH = os.environ.get("LOCAL_BUILD_PATH")
WORLD_BUILD_PATH = os.environ.get("WORLD_BUILD_PATH")

# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.8",
        LOCAL_BUILD_PATH
    ).build_dev() as pack:
    
    startup_item = Items.WARPED_FUNGUS_ON_A_STICK

    @pack.mcfn(sort="load")
    def load():
        cmd.Log.info(f"Pack '{pack._pack_name}' Loaded!")
        give_initial_item()
    
    @pack.mcfn(path="utils")
    def give_initial_item():
        cmd.TellRaw("a", f"Giving players {Items.NAME_TAG.display_name}")
        cmd.Command(f"give @s {startup_item}")