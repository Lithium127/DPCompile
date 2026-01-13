import os
from src.dpc import PackDSL, cmd
from src.dpc.plugin.verbose_logging import VerboseLoggingPlugin
from src.dpc.plugin.development_kit import DevelopmentKit

from src.dpc import Entities, S
from src.dpc import Script


# Pack Creation
with PackDSL(
        "Testing Pack", "tcev", 
        "This is a test description", 
        "1.21.8",
        os.environ.get("LOCAL_BUILD_PATH")
    ).build_dev().with_plugins(
        VerboseLoggingPlugin(file = False),
        DevelopmentKit()
    ) as pack:
    
    @pack.mcfn(sort="load")
    def load():
        cmd.Log.info(f"'{pack.name}' Loaded! Using namespace '{pack.namespace}'.")