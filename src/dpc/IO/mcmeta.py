from __future__ import annotations
import typing as t

from enum import Enum
import json

from .jsonfile import JsonFile
from ..datatypes import Version, VersionError


class Feature(Enum):
    "A list of current and past experimental changes to minecraft."
    
    MINECART_IMPROVEMENTS = "minecraft:minecart_improvements"
    """Changes behavior of minecarts, allowing them to move faster and more smoothly (among other changes)."""
    
    REDSTONE_EXPERIMENTS = "minecraft:redstone_experiments"
    """Changes behavior of redstone circuits, tweaking some aspects based on directionality or randomness, and how the redstone wire interacts with other blocks."""
    
    VILLAGER_REBALANCE = "minecraft:trade_rebalance"
    
    LOCATOR = "minecraft:locator_bar"
    """Adds a locator bar to show the positions of other players in multiplayer."""

class McMeta(JsonFile):
    """Represents a metadata file that describes information within a pack. Enabling
    optional game content or overriding information based on versioning.
    """
    description: str
    supported_formats: int | tuple[int, int] | None
    features: list[str]
    filters: list[tuple[str, str]] # TODO: Make first argument in feature tuples use namespace type
    overlays: list[tuple[str, int | tuple[int, int]]]
    # TODO: Metadata holds the location of pack.png file
    
    FEATURES = Feature
    
    def __init__(self,
                 description: str,
                 *,
                 supported_format: int | tuple[int, int] | None = None,
                 features: list[str] = [],
                 filters: list[tuple[str, str]] = [],
                 overlays: list[tuple[str, int | tuple[int, int]]] = []):
        """Represents metadata attached to a given datapack, tells the game what features
        are required to make this pack operate properly and what sections to filter from
        the pack. Also capable of enabling optional features.
        
        The pack meta is handled by the pack context through the `PackDSL` object, which holds pack
        context at any given moment. This allows commands and ideas like versioning hotfixes to
        by dynamically applied when required instead of manually fixing versions. Whenever a `@version_overload(...)`
        script is created it loads itself into the `overlays` list through the pack at compile time.
        
        All packs created through the `PackDSL` require the metadata be passed at pack init, as the
        metadata holds the namespace and name.

        Args:
            description (str): The decription of this pack.
            pack_format (int): The format of the pack, this is taken from version range.
            supported_format (int | tuple[int, int] | None): The range of formats that are supported by this pack
            features (list[str]): List of flags for enabling optional experimental features if those are required by this pack
            filters (list[tuple[str, str]]): The list of files to filter out from packs that are applied below this one in the order. If any 
                                                file matches one of the patterns given it is treated as if it was not present in the pack at 
                                                all. Enables overriding other pack information
            overlays (list[tuple[str, int  |  tuple[int, int]]]): Selection of overlays, given `(<directory>, <format(s)>)` where the directory 
                                                                    is the directory to overlay for the respective versions. Essentially allows 
                                                                    for version specific hacks and fixes to exist and override other information. 
                                                                    The format range is given as a single integer version or as a range of 
                                                                    values. The order of this argument matters as the first available item is 
                                                                    applied first.
        """
        super().__init__(
            name = "pack.mcmeta"
        )
        self.description = description
        self.supported_formats = supported_format
        self.features = features
        self.filters = filters
        self.overlays = overlays
    
    def render(self):
        pack_version_reference = self.pack.version.pack_reference
        if pack_version_reference == -1:
            raise VersionError(f"Requested Pack version not found within pack reference number, version {self.pack.version}")
        content = {
            "pack" : {
                "description" : self.description,
                "pack_format" : pack_version_reference,
            }
        }
        # Add optional supported formats
        if self.supported_formats is not None:
            content["pack"]["supported_formats"] = self.supported_formats if isinstance(self.supported_formats, int) else {
                "min_inclusive": self.supported_formats[0],
                "max_inclusive": self.supported_formats[1]
            }
        
        # Add optional filters
        if len(self.filters) > 0:
            content["filter"] = {
                "block" : [
                    {
                        "namespace" : e[0],
                        "path" : e[1]
                    } for e in self.filters
                ]
            }
        
        # Add features
        if len(self.features) > 0:
            content["features"] = {
                "enabled" : [
                    feature for feature in self.features
                ]
            }
        
        if len(self.overlays) > 0:
            content["overlays"] = {
                "entries" : [
                    {
                        "directory" : e[0],
                        "formats" : e[1] if isinstance(e[1], int) else {
                            "min_inclusive": e[1][0],
                            "max_inclusive": e[1][1]
                        }
                    } for e in self.overlays
                ]
            }
        
        return json.dumps(content, indent=self.indent)
    
    def require_feature(self, feature: str | Enum) -> None:
        """Adds a feature to the list of required features

        Args:
            feature (str): The title of the feature. See Feature enum for list of available experiments
        """
        self.features.append(feature if isinstance(feature, str) else feature.value)

    def add_overlay(self, directory: str, format: int | tuple[int, int], index = None) -> None:
        """Adds an overlay to the registered list, which are sub-packs applied over the "normal" contents of a pack. 
        Their directories have their own assets and data directories, and are placed in the pack's root directory. 
        The order is important, as the first in the list is applied first.

        Args:
            directory (str): The directory to overlay for the respective version
            format (int | tuple[int, int]):  Describes a range for pack formats when this overlay should be active.
            index (int, optional): The index to place this overlay in, higher values are higher priorety. Defaults to None.
        """
        entry = (directory, format)
        if index is None:
            self.overlays.append(entry)
        else:
            self.overlays.insert(index, entry)
    
    def add_filter(self, namespace: str, path: str) -> None:
        """Enables this pack to selectively filter out content
        from other sources (Including the base game). Provided
        a namespace to select content from and a path to the
        resource being masked

        Args:
            namespace (str): The namespace for that resource
            path (str): The path to the resource being masked
        """
        self.filters.append((namespace, path))