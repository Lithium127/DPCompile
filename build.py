import os

from src.dpc import Datapack

pack = Datapack(
    pack_name   = "Testing Pack",
    namespace   = "tp",
    build_path  = os.path.dirname(os.path.realpath(__file__)),
    description = "Pack for testing the DPCompile script, does not do anything important",
    version     = "1.20.1"
)

pack.build()