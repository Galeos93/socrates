import pytest
from unittest.mock import Mock

from application.use_cases.document_ingestion import IngestDocumentUseCase
from domain.entities.document import Document, DocumentID


class TestIngestDocumentUseCase:
    """Tests for document ingestion use case."""

    @pytest.fixture
    def mock_parser(self):
        """Create a mock document parser."""
        parser = Mock()
        # Mock parser returns a Document
        doc = Document(
            id=DocumentID("test-doc-123"),
            text="Extracted document text",
            metadata={"filename": "test.pdf"}
        )
        parser.parse.return_value = doc
        return parser

    @pytest.fixture
    def mock_repository(self):
        """Create a mock document repository."""
        return Mock()

    @pytest.fixture
    def use_case(self, mock_parser, mock_repository):
        """Create use case instance."""
        return IngestDocumentUseCase(
            document_parser=mock_parser,
            document_repository=mock_repository
        )

    @staticmethod
    def test_execute_calls_parser(use_case, mock_parser):
        """Test that execute calls the parser with correct arguments."""
        file_bytes = b"pdf content"
        filename = "document.pdf"
        
        use_case.execute(file_bytes, filename)
        
        mock_parser.parse.assert_called_once_with(file_bytes, filename)

    @staticmethod
    def test_execute_saves_document(use_case, mock_parser, mock_repository):
        """Test that execute saves the parsed document."""
        file_bytes = b"pdf content"
        filename = "document.pdf"
        
        use_case.execute(file_bytes, filename)
        
        # Verify repository save was called
        assert mock_repository.save.called
        saved_doc = mock_repository.save.call_args[0][0]
        assert isinstance(saved_doc, Document)
        assert saved_doc.id == DocumentID("test-doc-123")

    @staticmethod
    def test_execute_returns_document_id(use_case):
        """Test that execute returns the document ID."""
        file_bytes = b"pdf content"
        filename = "document.pdf"
        
        document_id = use_case.execute(file_bytes, filename)
        
        assert document_id == DocumentID("test-doc-123")

    @staticmethod
    def test_execute_propagates_parser_errors(use_case, mock_parser):
        """Test that parser errors are propagated."""
        mock_parser.parse.side_effect = ValueError("Unsupported format")
        
        with pytest.raises(ValueError) as exc_info:
            use_case.execute(b"content", "bad.txt")
        
        assert "Unsupported format" in str(exc_info.value)
