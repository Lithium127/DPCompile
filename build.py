import os

from src.dpc import Datapack, Module, cmd, BlockPosition, EntityData

test = EntityData()


from src.dpc.shortcuts.item import DPItem

pack = Datapack(
    pack_name   = "Testing Pack",
    namespace   = "testingpack",
    build_path  = os.path.dirname(os.path.realpath(__file__)),
    description = "Pack for testing the DPCompile script, does not do anything important",
    version     = "1.21.1"
)

@pack.tick("tick")
def reset():
    return [
        "# --< Update >-- #"
    ]

@pack.script("something_cool")
def test():
    return [
        cmd.Execute().align("xyz").as_()
    ]

plr_teleporter = DPItem("home_tp", pack)

pack.build()