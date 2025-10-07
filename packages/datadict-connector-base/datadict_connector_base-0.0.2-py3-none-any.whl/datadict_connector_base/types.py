from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ItemType(str, Enum):
    """
    Enum for item types that control frontend rendering and business logic.
    """

    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    DOC = "doc"
    TEST = "test"
    LOGIC = "logic"
    CONFIG = "config"


class ChangeType(str, Enum):
    """
    Enum for sync change operations.
    """

    CREATE = "create"
    MODIFY = "modify"
    ARCHIVE = "archive"
    UNARCHIVE = "unarchive"


class CatalogType(str, Enum):
    """
    Enum for catalog types.
    """

    DATABASE = "database"
    DBT = "dbt"


class ItemChange(BaseModel):
    """
    Represents a single change operation to synchronize local metadata with remote.
    """

    id: Optional[str] = None
    change: ChangeType

    type: Optional[str] = None
    name: Optional[str] = None
    key: Optional[str] = None
    sub_type: Optional[str] = None
    data_type: Optional[str] = None
    parent_key: Optional[str] = None
    parent_id: Optional[str] = None

    depth: Optional[int] = None


class PhysicalChangeRequest(BaseModel):
    """
    Provides a note on what needs to be physically applied on filesystem.
    """

    path: str  # Path from catalog root
    action: str  # (set / delete)
    content: str
