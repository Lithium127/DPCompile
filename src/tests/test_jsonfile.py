import pytest
from src.dpc import JsonFile
from src.dpc import PackDSL


def test_json_file_name():
    instance = JsonFile("test")
    assert instance.name == "test"

def test_json_pack_parent(pack: PackDSL, pack_namespace):
    instance = JsonFile("test")
    file_path = f"data/{pack_namespace}/json"
    pack.register_file(file_path, instance)
    assert instance.pack is pack
    assert instance in pack.directory.get_files(file_path)