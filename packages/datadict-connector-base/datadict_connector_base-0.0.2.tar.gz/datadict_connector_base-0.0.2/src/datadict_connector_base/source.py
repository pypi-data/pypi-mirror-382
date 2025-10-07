from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pandas as pd


class MetadataSource(ABC):
    """
    Abstract base class for all metadata sources.

    This class defines the interface that all metadata sources must implement
    to work with the DataDict sync system.
    """

    @abstractmethod
    def read_metadata(self) -> pd.DataFrame:
        """
        Read metadata from the source and return as pandas DataFrame compatible with sync system.

        Returns:
            DataFrame with columns required by sync system:
            - type: Item type (database, schema, table, column)
            - name: Item name
            - key: Fully qualified name (e.g., "database.schema.table")
            - sub_type: Optional subtype classification
            - data_type: Data type information (for columns)
            - parent_key: Parent item's FQN (null for root items)
        """
        pass

    @abstractmethod
    def set_credentials(self, credentials: Dict[str, Any]) -> None:
        """
        Set connection credentials for the metadata source.

        Args:
            credentials: Dictionary containing connection parameters specific to the source
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close any open connections or resources.

        This method should be called when the metadata source is no longer needed
        to ensure proper cleanup of resources.
        """
        pass

    def read_lineage(self) -> Optional[pd.DataFrame]:
        """Optional hook to fetch lineage relationships from the source."""
        return None
