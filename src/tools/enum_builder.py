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
        arguments.append(f"{var} = {val}")
    return f"{block_name.upper()} = Block({', '.join(arguments)})\n"

with open(DATA_PATH, "r") as reader:
    data = json.load(reader)

with open(BLOCK_ENUM_PATH, "w") as writer:
    writer.write("")

with open(BLOCK_ENUM_PATH, "a") as writer:
    indent = 0
    writer.write("from enum import Enum\n\nfrom .. import Block\n\n")
    writer.write("class Blocks(Enum):\n")
    indent = 1

    for entry in data:
        writer.write(("\t" * indent) + load_block(entry))