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
        Weapon()
    
    @pack.mcfn(path = "utils")
    def give_initial_item():
        cmd.TellRaw("a", f"Giving players {Items.NAME_TAG.display_name}")
        cmd.Command(f"give @s {startup_item}")
    
    @pack.mcfn(path="utils")
    def clear_entities(): pass
    

    class Weapon(Template):
        
        name: str

        @script(sort="load")
        def initialize(self) -> None:
            cmd.Comment("This is where the on hit and on kill scoreboards are created")

        @script()
        def give(self) -> None:
            cmd.Comment("Clear previous items from player inventory")
        
        def _identifier(self):
            return "@e[type=item, tag=tcev_weapon, limit=1]"

    @pack.template("weapons/bow")
    class Bow(Weapon):
        
        @script()
        def give(self) -> None:
            # This function is in multiple places
            Sword().on_kill()

        @script()
        def on_arrow_hit(self) -> None:
            cmd.Comment(f"Referencing {self.__class__.__name__}")
            cmd.Command(f"execute as @p at @s run execute as", self, f"at @s run {cmd.TellRaw('a', 'arrow hit')}")
    
    @pack.template("weapons/sword")
    class Sword(Weapon):

        @script(mask_if_empty=False)
        def on_kill(self) -> None: pass