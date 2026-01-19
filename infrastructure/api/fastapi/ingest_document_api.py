from dataclasses import dataclass

from fastapi import UploadFile, File, HTTPException
from pydantic import BaseModel

from application.use_cases.document_ingestion import IngestDocumentUseCase


class IngestDocumentResponse(BaseModel):
    """Response model for document ingestion."""
    document_id: str
    filename: str
    message: str


@dataclass
class IngestDocumentAPIBase:
    """Base API for document ingestion endpoint."""
    
    ingest_document_use_case: IngestDocumentUseCase

    async def ingest_document(self, file: UploadFile = File(...)) -> IngestDocumentResponse:
        """
        Ingest a document file (PDF) and extract its text.

        Parameters
        ----------
        file : UploadFile
            The uploaded document file.

        Returns
        -------
        IngestDocumentResponse
            Response containing the document ID and metadata.

        Raises
        ------
        HTTPException
            If the file format is unsupported or parsing fails.
        """
        try:
            # Read file bytes
            file_bytes = await file.read()
            filename = file.filename or "unknown.pdf"

            # Execute use case
            document_id = self.ingest_document_use_case.execute(
                file_bytes=file_bytes,
                filename=filename
            )

            return IngestDocumentResponse(
                document_id=str(document_id),
                filename=filename,
                message="Document ingested successfully"
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")
