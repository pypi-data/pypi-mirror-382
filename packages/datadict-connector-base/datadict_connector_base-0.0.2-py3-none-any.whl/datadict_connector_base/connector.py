from abc import ABC, abstractmethod

from .applier import ChangeApplier
from .loader import CatalogLoaderV2
from .path_builder import PathBuilder
from .source import MetadataSource


class ConnectorBase(ABC):
    """
    Base connector class that provides factory methods for creating
    loader, applier, path builder, and metadata source instances.
    """

    @abstractmethod
    def make_loader(self) -> CatalogLoaderV2:
        """
        Create a catalog loader instance.

        Returns:
            CatalogLoaderV2 instance
        """
        pass

    @abstractmethod
    def make_path_builder(self, lookup_table: dict[str, str]) -> PathBuilder:
        """
        Create a path builder instance.

        Args:
            lookup_table: Dict mapping FQN keys to existing file paths

        Returns:
            PathBuilder instance
        """
        pass

    @abstractmethod
    def make_applier(self) -> ChangeApplier:
        """
        Create a change applier instance.

        Returns:
            ChangeApplier instance
        """
        pass

    @abstractmethod
    def make_source(self) -> MetadataSource:
        """
        Create a metadata source instance.

        Returns:
            MetadataSource instance
        """
        pass
