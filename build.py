import os
from src.dpc import PackDSL, cmd, Blocks, Items, TagTable
from src.dpc.plugin.verbose_logging import VerboseLoggingPlugin

# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.8",
        os.environ.get("LOCAL_BUILD_PATH")
    ).build_dev().with_plugins(
        VerboseLoggingPlugin(file=False)
    ) as pack:
    
    startup_item = Items.WARPED_FUNGUS_ON_A_STICK
    scaffold_blocks = TagTable('block', "scaffold", [
        Blocks.ANDESITE,
        Blocks.IRON_BLOCK, 
        Blocks.IRON_BARS,
        Blocks.STONE, 
    ])
    pack.add_tag_table(scaffold_blocks)

    @pack.mcfn(sort = "load")
    def load():
        cmd.Log.info(f"Pack '{pack._pack_name}' Loaded!")
        give_initial_item()
    
    @pack.mcfn(path = "utils")
    def give_initial_item():
        cmd.TellRaw("a", f"Giving players {Items.NAME_TAG.display_name}")
        cmd.Command(f"give @s {startup_item}")
    
    @pack.mcfn(path="utils")
    def clear_entities():
        cmd.Comment("Nothing here yet")
    
