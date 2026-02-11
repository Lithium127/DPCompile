from __future__ import annotations
import typing as t

from .packfile import PackFile


class MCFunctionFile:
    """Represents an externally loaded function file, 
    for example from another datapack. These files can
    be included in scripts as either embeddeings, links, 
    or snippets, see function documentation for more 
    information.
    
    Files will be loaded from anywhere the path points to.
    local files default to execution directory."""

    _resource_location: str
    _content_cache: str | None

    def __init__(self, path):
        self._content_cache = None


    def content(self) -> str:
        """Returns the content stored in this resource."""
        if self._content_cache is None:
            with open(self._resource_location, "r") as f:
                self._content_cache = f.read()
        
        return self._content_cache