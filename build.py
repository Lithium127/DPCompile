import os
from src.dpc import PackDSL, cmd, Module, modulemethod, Script, Blocks, mc_advancement, Advancement

LOCAL_BUILD_PATH = os.environ.get("LOCAL_BUILD_PATH")
WORLD_BUILD_PATH = os.environ.get("WORLD_BUILD_PATH")

print(LOCAL_BUILD_PATH)

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
        cmd.Comment(f"Testing command with build issues:\n {cmd.TellRaw('a', cmd.TellRaw('a', 'this is a test').build())}")

        """ This method has problems
        Currently commands passed as arguments caught as if they were in the
        code structure of the function itself, however this is undesirable as
        the content of these commands will be added multiple times

        Example Output:
            # This script was automatically generated for [Testing Pack]
            # MC Version: 1.21.4 [61]
            # ---
            # Grows vines downward from targeted logs

            # this is a test
            tellraw @a {"text": "# this is a test"}
            # Testing command with build issues:
            #  <src.dpc.cmd.command.TellRaw object at 0x0000016D9DD4F100>
        """
    
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
    
    @pack.mcfn(dev=True)
    def spawn_tree_at_player():
        """Spawns a tree at the location of the current player"""
        cmd.Log.info("Spawned tree at player location")
        cmd.Command("execute at @s as @s run " + birch.spawn(register=False).build())

@mc_advancement(title = "Enter the Nether")
def enter_nether(instance: Advancement):
    """Description is pulled from here"""
    instance.rewards.set_script(birch.spawn)


enter_nether.render()

print("\n".join([f"{entry} : {enter_nether.__dict__[entry]}" for entry in enter_nether.__dict__.keys()]))