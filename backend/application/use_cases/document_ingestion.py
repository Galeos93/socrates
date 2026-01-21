from dataclasses import dataclass
import logging

from domain.entities.document import Document, DocumentID
from domain.ports.document_parser import DocumentParser
from domain.ports.document_repository import DocumentRepository


@dataclass
class IngestDocumentUseCase:
    """
    Use case for ingesting raw document bytes and converting them to Document entities.
    
    This orchestrates:
    1. Parsing raw bytes into a Document with extracted text (via DocumentParser)
    2. Persisting the Document (via DocumentRepository)
    """

    document_parser: DocumentParser
    document_repository: DocumentRepository

    def execute(self, file_bytes: bytes, filename: str) -> DocumentID:
        """
        Ingest a document by parsing its bytes and storing it.

        Parameters
        ----------
        file_bytes : bytes
            Raw bytes of the document file.
        filename : str
            Original filename including extension (e.g., "document.pdf").

        Returns
        -------
        DocumentID
            The ID of the newly created Document entity.

        Raises
        ------
        ValueError
            If the file format is not supported or parsing fails.
        """
        logging.info("[IngestDocumentUseCase] Starting document ingestion.")

        # Parse raw bytes into Document entity
        document = self.document_parser.parse(file_bytes, filename)

        # Persist the document
        self.document_repository.save(document)

        return document.id
