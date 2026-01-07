import os
from src.dpc import PackDSL, cmd, Blocks, Items, TagTable
from src.dpc.plugin.verbose_logging import VerboseLoggingPlugin
from src.dpc import Template, script
# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.8",
        os.environ.get("LOCAL_BUILD_PATH")
    ).build_dev().with_plugins(
        VerboseLoggingPlugin(file=False)
    ) as pack:
    
    @pack.mcfn(sort="load")
    def load():
        clone_rift = cmd.Clone(
            (0, 0, 0), (3, 3, 3), (0, 100, 0), 
            Blocks.NETHERRACK, "move",
            source_dim="minecraft:the_nether",
            dest_dim="minecraft:overworld"
        )
        cmd.Comment(f"Clone rift from {clone_rift.source_dim} with a volume of {clone_rift.volume} blocks")
        clone_rift()