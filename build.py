from src.dpc import PackDSL, cmd, Script, Scoreboard, Selector, TextElement

WORLD_BUILD_PATH = "C:/Users/lman_/AppData/Roaming/.minecraft/saves/DPCompile Testing World/datapacks"
LOCAL_BUILD_PATH = "C:/Users/lman_/Personal Projects/python/DPCompile"

meta_boards = [
    "is_sneaking", "in_air"
]

# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.4",
        LOCAL_BUILD_PATH,
        dev = False
    ) as pack:
    
    @pack.mcfn(sort="load")
    def load():
        cmd.Log.info("Pack loaded properly")
        intro_msg()
        display_version_information()
    
    @pack.mcfn()
    def intro_msg():
        cmd.Log.info("Displaying intro message")
        message = TextElement(f"-=<[ {pack._pack_name} - {pack.version}]>=-")
        cmd.Command(f"tellraw @a {message}")
    
    @pack.mcfn(dev=True)
    def display_version_information():
        cmd.Log.info(f"VersionL {pack.version} [{pack.version.pack_reference}]")