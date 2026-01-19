from abc import ABC, abstractmethod

from domain.entities.document import Document


class DocumentParser(ABC):
    """Port interface for parsing raw document bytes into Document entities."""

    @abstractmethod
    def parse(self, file_bytes: bytes, filename: str) -> Document:
        """
        Parse raw document bytes into a Document entity with extracted text.

        Parameters
        ----------
        file_bytes : bytes
            Raw bytes of the document file.
        filename : str
            Original filename including extension (e.g., "document.pdf").

        Returns
        -------
        Document
            Document entity with extracted text content.

        Raises
        ------
        ValueError
            If the file format is not supported.
        """
        pass
