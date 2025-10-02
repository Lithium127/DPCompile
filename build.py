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
        

# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.4",
        LOCAL_BUILD_PATH,
        dev = True
    ) as pack:
    
    test = TreeModule("oak", 60)
    pack.mount(test, "trees")
    
    @pack.mcfn(sort="load")
    def load():
        cmd.Log.info("Pack loaded")
        # Causes problems, not replaced with call to Script.__call__() which produces the
        # `function <path_to_script>` command
        test.spawn()