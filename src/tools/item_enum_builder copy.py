"""
Helper script for generating the `dpc.datatypes.enum.block` enum

Data generated from block.json file found from PrismarineJS repo
https://github.com/PrismarineJS/minecraft-data/blob/master/data/pc/1.21.8/items.json
"""

import json

BLOCK_ENUM_PATH = "C:\\Users\\Liam\\Documents\\Personal Projects\\Python\\DPCompile\\src\\dpc\\datatypes\\enum\\item_enum.py"
DATA_PATH = "C:\\Users\\Liam\\Documents\\Personal Projects\\Python\\DPCompile\\src\\tools\\items.json"
requested_data = (
    ("item_number" , "id"),
    ("id" , "name"),
    ("display_name", "displayName"),
    # ("stack_size", "stackSize")
)

def load_block(data: dict) -> str:
    block_name: str = data.get("name", "NOT_FOUND")
    print(f"Generating for {block_name}")

    arguments = []
    for var, val in requested_data:
        val = data.get(val)
        if isinstance(val, str):
            val = f'"{val}"'
        arguments.append(f"\"{var}\" : {val}")
    arguments.append(f"\"namespace\" : \"minecraft\"")
    return block_name.upper() + ": Item = {" + ', '.join(arguments) + "}\n"

with open(DATA_PATH, "r") as reader:
    data = json.load(reader)

with open(BLOCK_ENUM_PATH, "w") as writer:
    writer.write("")

with open(BLOCK_ENUM_PATH, "a") as writer:
    indent = 0
    writer.write("from ..item import Item\n")
    writer.write("from .metaenum import EnumMeta\n\n")
    writer.write("class Items(metaclass = EnumMeta):\n\t_type_as = Item\n")
    indent = 1

    for entry in data:
        writer.write(("\t" * indent) + load_block(entry))