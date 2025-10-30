import os
from src.dpc import PackDSL, cmd, Module, modulemethod, Script, Blocks

from src.dpc.datatypes.enum.item_enum import Items

LOCAL_BUILD_PATH = os.environ.get("LOCAL_BUILD_PATH")
WORLD_BUILD_PATH = os.environ.get("WORLD_BUILD_PATH")

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
        cmd.Comment(f"This is where the {initialize} function runs")
        initialize()
    
    @pack.mcfn(path="util/startup")
    def initialize(script):
        """Performs required startup for all groups"""
        cmd.Log.info("Initializing via {self}")
    
    @pack.mcfn(path="util/data")
    def make_stationary():
        """Makes a selected entity stationary"""
        cmd.Log.info("Making entity.current stationary")