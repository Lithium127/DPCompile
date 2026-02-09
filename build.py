import os
from src.dpc import PackDSL, cmd
from src.dpc.plugins import VerboseLoggingPlugin

from src.dpc import Entities, S
from src.dpc import Script
from src.dpc import Pos


with PackDSL("Testing Pack", "tcev", 
        "description", "1.21.8",
        os.environ.get("LOCAL_BUILD_PATH")
    ).with_plugins(
        VerboseLoggingPlugin()
    ).build_dev() as pack:
    

    @pack.mcfn()
    def load():
        cmd.Log.info(f"'{pack.name}' loaded using namespace '{pack.namespace}'.")
