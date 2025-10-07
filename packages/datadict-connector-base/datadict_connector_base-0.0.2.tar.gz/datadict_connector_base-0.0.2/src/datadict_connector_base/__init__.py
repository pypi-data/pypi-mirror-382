"""
DataDict Connector Base Package

Provides base classes and types for building DataDict connectors.
"""

__version__ = "0.0.1"

from .applier import ChangeApplier
from .connector import ConnectorBase
from .loader import CatalogItem, CatalogLoaderV2
from .path_builder import PathBuilder
from .source import MetadataSource
from .types import CatalogType, ChangeType, ItemChange, ItemType, PhysicalChangeRequest
from .util import (
    dump_yaml_string,
    load_yaml_files_from_directory,
    parse_yaml_string,
    read_yaml_file,
    write_yaml_file,
)

__all__ = [
    "ItemType",
    "ChangeType",
    "CatalogType",
    "ItemChange",
    "PhysicalChangeRequest",
    "CatalogItem",
    "CatalogLoaderV2",
    "ChangeApplier",
    "PathBuilder",
    "MetadataSource",
    "ConnectorBase",
    "parse_yaml_string",
    "dump_yaml_string",
    "read_yaml_file",
    "write_yaml_file",
    "load_yaml_files_from_directory",
]
