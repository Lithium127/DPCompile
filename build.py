from src.dpc import PackDSL, cmd, Script, Scoreboard, Selector, TextElement, ScoreCriteria

WORLD_BUILD_PATH = "C:/Users/lman_/AppData/Roaming/.minecraft/saves/DPCompile Testing World/datapacks"
LOCAL_BUILD_PATH = "C:/Users/lman_/Personal Projects/python/DPCompile"

plr_data = [
    "is_sneaking", "in_air"
]

# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.4",
        LOCAL_BUILD_PATH,
        dev = True
    ) as pack:
    
    Scoreboard("is_sneaking", criteria=ScoreCriteria.player_kill_count())
    
    @pack.mcfn(sort="load")
    def load():
        cmd.Log.info("Pack loaded properly")
    
    @pack.mcfn(sort="tick")
    def tick():
        update_positions()
        reset_scores()
    
    @pack.mcfn()
    def reset_scores():
        Scoreboard("is_sneaking").reset(Selector.ALL())
    
    def update_positions():
        # Replace with data set command
        # Ex: execute store result score @a tcev_plr_x run data get position[0]
        cmd.Comment("Updating player coordinate tracking")
        Scoreboard("plr_x").set_value(Selector.ALL(), 5)
        Scoreboard("plr_y").set_value(Selector.ALL(), 5)
        Scoreboard("plr_z").set_value(Selector.ALL(), 5)