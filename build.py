from src.dpc import PackDSL, cmd, Module, modulemethod, Script, Blocks

LOCAL_BUILD_PATH = "C:\\Users\\Liam\\Documents\\Personal Projects\\Python\\DPCompile"

class TreeModule(Module):
    
    split_angle: int
    
    def __init__(self, name: str, split_angle: int, **kwargs):
        super().__init__(name, **kwargs, mnt_path="trees")
        self.split_angle = split_angle
    
    @modulemethod()
    def spawn(self):
        """Spawns a tree at the current position"""
        cmd.Log.info(f"Spawned tree of type [{self._module_name}]")
    
    @modulemethod()
    def place_foliage(self):
        """Places a randomly generated leaf at this location"""
        cmd.Log.info("Placing some kind of leaf here")
    
    @modulemethod()
    def place_vines(self):
        """Grows vines downward from targeted logs"""
        # cmd.Comment("")
    
    @modulemethod()
    def propogate(self):
        """Recursive call for generating """
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
    
    oak = TreeModule("oak", 60, parent = pack)
    birch = TreeModule("birch", 78, parent = pack)
    
    @pack.mcfn(sort="load")
    def load():
        cmd.Log.info("Pack loaded")
        cmd.Log.warn(f"Warning for {Blocks.STONE_BRICKS}")
    
    @pack.mcfn(dev=True)
    def spawn_tree_at_player():
        """Spawns a tree at the location of the current player"""
        cmd.Log.info("Spawned tree at player location")
        cmd.Command("execute at @s as @s run " + birch.spawn(register=False).build())