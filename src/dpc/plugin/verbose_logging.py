import os

from .dpc_plugin import DPCPlugin

from ..IO.script import Script

class VerboseLoggingPlugin(DPCPlugin):
    """**[Builtin]** Plugin that displays information to the console 
    during the build process, including file content, final directory
    layout, and exceptions during rendering.
    """

    display: dict[str, bool]

    def __init__(self, directory: bool = True, file: bool = True):
        """Plugin that displays information to the console during the build
        process.

        Args:
            directory (bool, optional): If the final directory layout should be displayed. Defaults to True.
            file (bool, optional): If files should be printed to the console after rendering. Defaults to True.
        """
        self.display = {
            "file" : file,
            "dir" : directory
        }

    def render_file(self, pack, file, path):

        if not self.display.get("file", False):
            return None
        
        content = file.render()
        if content is not None:
            print(f"\n[{file.full_name}]{(' : Script' + (' instance passed' if file._pass_self else '')) if isinstance(file, Script) else ''}")
            print(f"  @ <{path}>")
            print("\n".join([f"  |  {line}" for line in content.split("\n")]))
    
    def post_build(self, pack):
        if not self.display.get("dir", False):
            return None
        
        # Display entire pack directory contents
        print("\nPack Contents:\n---")
        directory = {pack._pack_name : VerboseLoggingPlugin.dir_to_dict(pack._file_root)}

        def traverse_dir(tree, bars: list[bool] = [True]):
            for index, entry in enumerate(tree):

                child_marker = [(" | " if bar else "   ") for bar in bars[:-1]]
                bars[-1] = (index != len(tree)-1)
                entry_marker = (" | " if bars[-1] else " L ")
                print("".join(child_marker[1:]) + (entry_marker if len(bars) > 1 else "") + entry)

                if tree[entry] is not None:
                    traverse_dir(tree[entry], [*bars, True])
        
        traverse_dir(directory)
    
    @staticmethod
    def dir_to_dict(path):
            if not os.path.exists(path):
                raise FileNotFoundError(f"Path '{path}' does not exist.")
            if not os.path.isdir(path):
                raise NotADirectoryError(f"Path '{path}' is not a directory.")
            tree = {}
            try:
                for entry in os.listdir(path):
                    full_path = os.path.join(path, entry)
                    if os.path.isdir(full_path):
                        tree[entry] = VerboseLoggingPlugin.dir_to_dict(full_path)  # Recurse into subdirectory
                    else:
                        tree[entry] = None  # Files have None as value
            except PermissionError:
                tree["<Permission Denied>"] = None
            return tree