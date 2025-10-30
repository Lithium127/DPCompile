"""
Helper script for generating the `dpc.datatypes.enum.block` enum

Data generated from block.json file found from PrismarineJS repo
https://github.com/PrismarineJS/minecraft-data/blob/master/data/pc/1.21.8/blocks.json
"""

import json

BLOCK_ENUM_PATH = "C:\\Users\\Liam\\Documents\\Personal Projects\\Python\\DPCompile\\src\\dpc\\datatypes\\enum\\block_enum.py"
DATA_PATH = "C:\\Users\\Liam\\Documents\\Personal Projects\\Python\\DPCompile\\src\\tools\\blocks.json"
requested_data = (
    ("id" , "id"),
    ("name" , "name"),
    ("display_name", "displayName"),
    ("hardness", "hardness")
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
    return block_name.upper() + ": Block = {" + ', '.join(arguments) + "}\n"

with open(DATA_PATH, "r") as reader:
    data = json.load(reader)

with open(BLOCK_ENUM_PATH, "w") as writer:
    writer.write("")

with open(BLOCK_ENUM_PATH, "a") as writer:
    indent = 0
    writer.write("from ..block import Block\n\n")
    writer.write("""
class BlockMeta(type):
    def __delattr__(cls, name):
        raise AttributeError(f"Cannot delete attribute '{name}' from enum {cls.__name__}")
    
    def __setattr__(cls, name, val):
        raise AttributeError(f"Cannot modify attribute '{name}' from enum {cls.__name__}. Attempted value '{val}'")
    
    def __getattribute__(cls, name):
        data = super().__getattribute__(name)
        if isinstance(data, dict):
            instance = Block(**data)
            return instance
        return data\n\n""")
    writer.write("class Blocks(metaclass = BlockMeta):\n")
    indent = 1

    for entry in data:
        writer.write(("\t" * indent) + load_block(entry))