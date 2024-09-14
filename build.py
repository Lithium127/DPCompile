import os

from src.dpc import Datapack, Module, cmd, UUID, BlockPosition

pack = Datapack(
    pack_name   = "Testing Pack",
    namespace   = "testingpack",
    build_path  = os.path.dirname(os.path.realpath(__file__)),
    description = "Pack for testing the DPCompile script, does not do anything important",
    version     = "1.20.1"
)

@pack.tick("tick")
def reset():
    return [
        "# --< Update >-- #"
    ]

@pack.script("build_test")
def cloning():
    return [
        cmd.Clone(
            [10, 10, 10],
            [10, 20, 10],
            BlockPosition(0, 0, 0, relative=True)
        )
    ]

pack.build()