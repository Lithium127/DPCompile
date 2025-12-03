import pytest
from pathlib import Path

from src.dpc import PackDSL

@pytest.fixture
def pack_root():
    """Temporary datapack root directory."""
    return "/"

@pytest.fixture
def pack_name():
    return "Temp Pack"

@pytest.fixture
def pack_namespace():
    return "tmp"

@pytest.fixture
def pack_version():
    return "1.21.4"

@pytest.fixture
def pack(pack_name, pack_namespace, pack_version, pack_root):
    return PackDSL(
        pack_name = pack_name,
        namesapce = pack_namespace,
        description= "",
        version = pack_version,
        out_dir=pack_root
    )

@pytest.fixture
def pack_with_error_strict(pack):
    return pack.with_errors("strict")

@pytest.fixture
def make_file(pack_root):
    """Factory for constructing pack file objects with correct output paths."""
    def _make(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        return obj
    return _make