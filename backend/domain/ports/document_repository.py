from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities.document import Document


class DocumentRepository(ABC):
    """Repository interface for managing Document entities."""
    @abstractmethod
    def save(self, document: Document) -> None:
        """
        Persist a Document entity.

        Parameters
        ----------
        document : Document
            The Document entity to be saved.
        """
        pass

    @abstractmethod
    def get_by_id(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a Document by its ID.

        Parameters
        ----------
        document_id : str
            The unique identifier of the Document.

        Returns
        -------
        Optional[Document]
            The Document entity if found, otherwise None.
        """
        pass

    @abstractmethod
    def list_all(self) -> List[Document]:
        """
        List all Document entities.

        Returns
        -------
        List[Document]
            A list of all Document entities.
        """
        pass
