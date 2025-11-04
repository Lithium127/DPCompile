import os
from src.dpc import PackDSL, cmd, Blocks

LOCAL_BUILD_PATH = os.environ.get("LOCAL_BUILD_PATH")
WORLD_BUILD_PATH = os.environ.get("WORLD_BUILD_PATH")

# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.8",
        LOCAL_BUILD_PATH
    ).build_dev() as pack:
    
    @pack.mcfn()
    def get_block():
        cmd.Command(f"execute as @s at @s run {resolve_block_info()}")

    @pack.mcfn(path="util")
    def resolve_block_info():
        for block in Blocks.filter(lambda x: x.version.contains(pack.version)):
            message = f"Info for {block.display_name}; Source: {block.namespace}, Id: {block.id}, Name: {block.name}, Hardness: {block.hardness}"
            cmd.Command(f"execute if block ~ ~-1 ~ {block} run {cmd.TellRaw('s', message)}")