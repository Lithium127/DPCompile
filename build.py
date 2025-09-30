from src.dpc import PackDSL, cmd, Scoreboard, Selector, ScoreCriteria, Module, modulemethod, Script

LOCAL_BUILD_PATH = "C:\\Users\\Liam\\Documents\\Personal Projects\\Python\\DPCompile"

print(__package__)

class TreeModule(Module):
    
    split_angle: int
    
    def __init__(self, name: str, split_angle: int):
        super().__init__(name)
        self.split_angle = split_angle
    
    @modulemethod()
    def spawn(self):
        cmd.Log.info(f"Spawned tree of type [{self._module_name}]")
    
    @modulemethod()
    def propogate(self):
        cmd.Comment("This is where the recursing call for generating tree segments works")
        cmd.Comment(f"Split angle: {self.split_angle}")


class SpellModule(Module):
    
    cast_func: callable
    
    def __init__(self, name, cast_func: callable):
        super().__init__(name)
        self.cast_func = cast_func
    
    @modulemethod()
    def cast(self):
        cmd.Comment(f"The cast function for {self._module_name} spell")
        self.cast_func()
    
    @modulemethod()
    def give(self):
        cmd.Command("summon item ~ ~ ~")
    
    
        

# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.4",
        LOCAL_BUILD_PATH,
        dev = True
    ) as pack:
    
    test = SpellModule("test", lambda: cmd.Comment("Spell content go here"))
    pack.mount(test, "spells")
    
    @pack.mcfn(sort="load")
    def load():
        cmd.Log.info("Pack loaded")
    
    @pack.mcfn(sort="tick")
    def display_death_screen():
        """Displays a script when the player dies"""
        dead_players = Selector.ALL().if_score(Scoreboard("has_died", criteria=ScoreCriteria.death_count()), 1, operator=">")
        cmd.Command(f"execute as {dead_players} at @s if entity @s run " + cmd.Log.info("Detected player death", register=False).build())
        test.cast()
        Scoreboard("has_died").reset(dead_players)