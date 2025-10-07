from abc import ABC, abstractmethod
from typing import Dict, List

from .types import ItemChange, PhysicalChangeRequest


class ChangeApplier(ABC):
    """
    Base change applier that converts ItemChange objects into physical file operations.
    Does NOT execute the operations - returns requests that the caller can execute.
    """

    @abstractmethod
    def apply_change(
        self, change: ItemChange, lookup_table: Dict[str, str]
    ) -> List[PhysicalChangeRequest]:
        """
        Convert an ItemChange into a list of physical file change requests.

        Args:
            change: The change to apply
            lookup_table: Dict mapping FQN keys to existing file paths

        Returns:
            List of PhysicalChangeRequest objects representing file operations
        """
        pass
