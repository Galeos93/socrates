from typing import Dict, Optional, List

from domain.entities.document import Document
from domain.ports.document_repository import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    """
    In-memory implementation of DocumentRepository.

    Stores Document entities in a dictionary keyed by document ID.
    Intended for testing and local development.
    """

    def __init__(self) -> None:
        self._documents: Dict[str, Document] = {}

    def save(self, document: Document) -> None:
        """
        Persist a Document entity.
        """
        self._documents[document.id] = document

    def get_by_id(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a Document by its ID.
        """
        return self._documents.get(document_id)

    def list_all(self) -> List[Document]:
        """
        List all Document entities.
        """
        return list(self._documents.values())
