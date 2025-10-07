from typing import Dict, Optional

from .types import ItemType


class PathBuilder:
    """
    Helps locate existing file paths or generate default paths for items.
    Uses a lookup table to find files placed in non-standard locations.
    """

    def __init__(self, lookup_table: Dict[str, str]):
        """
        Initialize path builder with a lookup table.

        Args:
            lookup_table: Dict mapping FQN key -> existing file path
        """
        self.lookup_table = lookup_table

    def get_existing_path(self, key: str) -> Optional[str]:
        """
        Get the existing file path for a key from the lookup table.

        Args:
            key: Fully qualified name

        Returns:
            Existing file path or None if not found
        """
        return self.lookup_table.get(key)

    def get_default_path(self, key: str, item_type: ItemType) -> str:
        """
        Generate the default file path for a key.
        Must be implemented by subclasses.

        Args:
            key: Fully qualified name
            item_type: Type of the item

        Returns:
            Default file path relative to catalog root
        """
        raise NotImplementedError("Subclasses must implement get_default_path")

    def get_path(self, key: str, item_type: ItemType) -> str:
        """
        Get path for a key, preferring existing paths from lookup table.

        Args:
            key: Fully qualified name
            item_type: Type of the item

        Returns:
            File path relative to catalog root
        """
        existing = self.get_existing_path(key)
        if existing:
            return existing
        return self.get_default_path(key, item_type)
