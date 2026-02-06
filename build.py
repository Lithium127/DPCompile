import os
from src.dpc import PackDSL, cmd
from src.dpc.plugins import VerboseLoggingPlugin

from src.dpc import Entities, S
from src.dpc import Script
from src.dpc import Pos


# Pack Creation
with PackDSL("Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.8", os.environ.get("LOCAL_BUILD_PATH")
    ).build_dev(
    ).with_plugins(
        VerboseLoggingPlugin(file = False)
    ) as pack:
    
    @pack.mcfn(sort="load")
    def load():
        cmd.Log.info(f"'{pack.name}' Loaded! Using namespace '{pack.namespace}'.")
    
    @pack.mcfn()
    def abb_nether():
        cmd.Execute(abberate()).Positioned(Pos(0, 0, 0)).In("minecraft:the_nether")

    @pack.mcfn()
    def abberate():
        cmd.Clone(Pos(-3, -3, -3, "rel"), Pos(3, 3, 3, "rel"), Pos(3, 3, 3), dest_dim="minecraft:overworld")