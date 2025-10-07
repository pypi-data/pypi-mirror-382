from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel

from .types import ItemType


class CatalogItem(BaseModel):
    """
    Represents a single catalog item loaded from filesystem.
    This is a pure data model with no dependencies on Project/Catalog/DB.
    """

    name: str
    key: str
    parent_key: Optional[str] = None
    type: ItemType
    sub_type: Optional[str] = None
    data_type: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    properties: Dict = {}
    archived: bool = False
    file_path: Optional[str] = None


class CatalogLoaderV2(ABC):
    """
    Base catalog loader that loads items from file contents and returns them.
    Does NOT commit to database - that's the responsibility of the caller.
    Does NOT access filesystem - receives file contents as a dict.
    """

    @abstractmethod
    def load_from_files(self, files: Dict[str, str]) -> List[CatalogItem]:
        """
        Load all catalog items from file contents.

        Returns items in dependency order (parents before children).
        Does NOT persist items to database.

        Args:
            files: Dict mapping normalized file paths to file contents
                   Paths should use forward slashes and be relative to catalog root
                   Example: {"database.yml": "databases:\n  - name: mydb\n...",
                            "mydb/public/users.yml": "name: users\n..."}

        Returns:
            List of CatalogItem objects in dependency order
        """
        pass
