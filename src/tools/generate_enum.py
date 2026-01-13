"""Tool for generating class-based enumerations of minecraft data for use in
DPCompile. These tools are not intended to be served with the package and only
exist for creating generated classes within the pack.

Data for enums was pulled from files found from PrismarineJS minecraft-data repo
https://github.com/PrismarineJS/minecraft-data"""

import os
import json

def version_sources():
    for source in ["blocks", "entities", "items"]:
        make_versioned_source(source)

def build_enums():

    # Blocks
    build_enum_from_data(
        "Blocks",
        "Block",
        "blocks.json",
        ( # Requested Headers
            ("id" , "id"),
            ("name" , "name"),
            ("display_name", "displayName"),
            ("hardness", "hardness")
        ),
        [("..block", "Block")]
    )

    # Items
    build_enum_from_data(
        "Items",
        "Item",
        "items.json",
        ( # Requested Headers
            ("item_number" , "id"),
            ("id" , "name"),
            ("display_name", "displayName"),
            # ("stack_size", "stackSize")
        ),
        [("..item", "Item")]
    )

    # Entitys
    build_enum_from_data(
        "Entities",
        "Entity",
        "entities.json",
        ( # Requested Headers
            ("id", "internalId"),
            ("name", "name"),
            ("display_name", "displayName"),
            ("category", "category"),
            ("width", "width"),
            ("height", "height")
        ),
        [("..entity", "Entity")]
    )


# Internals

def build_enum_from_data(
        enum_name: str,
        enum_type: str,
        source: str,
        requested_headers: tuple[tuple[str, str],...],
        required_imports: list[tuple[str, str] | str],
        *,
        enum_root_path: str = "C:\\Users\\Liam\\Documents\\Personal Projects\\Python\\DPCompile\\src\\dpc\\datatypes\\enum\\",
        source_root_path: str = "C:\\Users\\Liam\\Documents\\Personal Projects\\Python\\DPCompile\\src\\tools\\sources",
        log_progress: bool = True,
        default_namespace: str = "minecraft"
):
    
    # Each line is a new string
    header: list[str] = list()
    
    # Set required imports
    for item in [*required_imports, (".metaenum", "EnumMeta")]:
        if isinstance(item, tuple):
            header.append(f"from {item[0]} import {item[1]}")
        else:
            header.append(f"import {item}")

    # Read in data for this class
    with open(f"{source_root_path}\\{source}", "r") as f:
        data: list[dict] = json.load(f)

    content: list[str] = list()

    # Create class header
    content.append(f"class {enum_name}(metaclass=EnumMeta[{enum_type}]):")

    # Data is list of entries with content
    for entry in data:
        entry_name: str = entry.get("name", "NOT_FOUND")
        if log_progress:
            print(f"Generating {enum_name}.{entry_name.upper()}")
        
        # Pull requested data
        arguments = {}
        for var, val in requested_headers:
            arguments[var] = entry.get(val)
        arguments["namespace"] = default_namespace
        if "versions" in entry:
            arguments["versions"] = (entry.get("versions")["min"], entry.get("versions")["max"])
        content.append(f"\t{entry_name.upper()}: {enum_type} = {arguments}")
            


    # Writing data
    with open(f"{enum_root_path}\\{enum_type.lower()}_enum.py", "w") as f:
        f.write("\n".join([*header, "\n", *content]))


def make_versioned_source(
        source_name: str,
        *,
        source_root_path: str = "C:\\Users\\Liam\\Documents\\Personal Projects\\Python\\DPCompile\\src\\tools\\sources",
        unversioned_root_path: str = "C:\\Users\\Liam\\Documents\\Personal Projects\\Python\\DPCompile\\src\\tools\\version_files"
):
    
    # List all files in a directory
    all_version_files: list[str] = [item for item in filter(
                    lambda x: os.path.isfile(f"{unversioned_root_path}\\{source_name}\\{x}"), 
                    os.listdir(f"{unversioned_root_path}\\{source_name}")
                   )]
    
    maintained_data: dict[str, dict] = {}

    # Files are named after the version their data is for
    for source in all_version_files:
        with open(f"{unversioned_root_path}\\{source_name}\\{source}", "r") as f:
            current_data: list[dict] = json.load(f)
        version = source.rstrip(".json")
        for entry in current_data:
            entry_name = entry.get("name")
            # Merge data
            if entry_name not in maintained_data:
                maintained_data[entry_name] = {}
            maintained_data[entry_name].update(entry)
            # Set version
            if "versions" not in maintained_data[entry_name]:
                maintained_data[entry_name]["versions"] = {
                    "min" : version,
                    "max" : None
                }
            maintained_data[entry.get("name")]["versions"]["max"] = version
    
    # Format dict to list
    data_format = [val for val in maintained_data.values()]

    # Output data to usable stream
    with open(f"{source_root_path}\\{source_name}.json", "w") as f:
        json.dump(data_format, f, indent=2)
    print(f"Versioned sources for '{source_name}'")



if __name__ == "__main__":
    version_sources()
    build_enums()