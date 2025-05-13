from src.dpc import PackDSL, Script, cmd, Scoreboard

WORLD_BUILD_PATH = "C:/Users/lman_/AppData/Roaming/.minecraft/saves/DPCompile Testing World/datapacks"
LOCAL_BUILD_PATH = "C:/Users/lman_/Personal Projects/python/DPCompile"

# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.4",
        LOCAL_BUILD_PATH
    ) as pack:
    
    @pack.mcfn(sort="load")
    def load():
        """Logs that the pack has loaded properly"""
        cmd.Log.info("Pack loaded!")
    
    @pack.mcfn()
    def raycast():
        cmd.Log.crit("This function is not yet implemented!")
    