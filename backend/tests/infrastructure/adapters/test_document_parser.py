import io
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock

from PIL import Image
import pytest

from infrastructure.adapters.document_parser import LLMOCRDocumentParser
from domain.entities.document import Document
from tests import resources

RESOURCES_FOLDER = Path(resources.__file__).parent


@pytest.fixture
def real_pdf_path() -> Path:
    """Path to a real PDF file for integration tests."""
    return RESOURCES_FOLDER / "test_document.pdf"


class TestLLMOCRDocumentParser:
    """Tests for LLM-based OCR document parser."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        client = Mock()
        response = Mock()
        response.choices = [Mock(message=Mock(content="Extracted text from page"))]
        client.chat.completions.create.return_value = response
        return client

    @pytest.fixture
    def parser(self, mock_openai_client):
        """Create parser instance with mock client."""
        return LLMOCRDocumentParser(client=mock_openai_client)

    @staticmethod
    def test_parse_rejects_non_pdf(parser):
        """Test that parser rejects non-PDF files."""
        file_bytes = b"fake content"
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse(file_bytes, "document.txt")
        
        assert "Unsupported file format" in str(exc_info.value)
        assert "Only PDF files are supported" in str(exc_info.value)

    @staticmethod
    def test_parse_rejects_docx(parser):
        """Test that parser rejects DOCX files."""
        file_bytes = b"fake content"
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse(file_bytes, "document.docx")
        
        assert ".docx" in str(exc_info.value)

    @staticmethod
    def test_image_to_base64(parser):
        """Test image to base64 conversion."""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        
        # Convert to base64
        base64_str = parser._image_to_base64(img)
        
        # Verify it's a non-empty string
        assert isinstance(base64_str, str)
        assert len(base64_str) > 0

    @staticmethod
    def test_extract_text_from_image_calls_openai(parser, mock_openai_client):
        """Test that text extraction calls OpenAI API correctly."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='blue')
        
        # Extract text
        text = parser._extract_text_from_image(img, page_num=1)
        
        # Verify OpenAI was called
        assert mock_openai_client.chat.completions.create.called
        call_args = mock_openai_client.chat.completions.create.call_args
        
        # Check model
        assert call_args.kwargs['model'] == 'gpt-4o'
        
        # Check messages structure
        messages = call_args.kwargs['messages']
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
        assert len(messages[0]['content']) == 2  # text + image
        
        # Verify extracted text
        assert text == "Extracted text from page"

    @staticmethod
    def test_parse_creates_document_with_metadata(parser, mock_openai_client, monkeypatch):
        """Test that parse creates a Document with proper metadata."""
        # Mock pdf2image to avoid needing actual PDF
        def mock_convert_from_bytes(pdf_bytes, dpi):
            # Return a single test image
            return [Image.new('RGB', (100, 100), color='green')]
        
        monkeypatch.setattr(
            'infrastructure.adapters.document_parser.convert_from_bytes',
            mock_convert_from_bytes
        )
        
        # Parse a "PDF"
        document = parser.parse(b"fake pdf bytes", "test_document.pdf")
        
        # Verify Document structure
        assert isinstance(document, Document)
        assert document.text == "Extracted text from page"
        assert document.metadata is not None
        assert document.metadata['filename'] == "test_document.pdf"
        assert document.metadata['num_pages'] == 1
        assert document.metadata['parser'] == "llm_ocr"


@pytest.mark.integration
class TestLLMOCRDocumentParserIntegration:
    """Integration tests with real OpenAI API (requires API key)."""

    @staticmethod
    @pytest.mark.skipif(
        os.getenv("OPENAI_API_KEY") is None,
        reason="Requires OPENAI_API_KEY environment variable"
    )
    def test_parse_real_pdf(real_pdf_path):
        """Test parsing a real PDF with OpenAI API."""
        from openai import OpenAI
        
        # This would require:
        # 1. A real OpenAI API key
        # 2. A real PDF file
        # 3. poppler-utils installed for pdf2image
        
        client = OpenAI()
        parser = LLMOCRDocumentParser(client=client)
        
        # Load a real PDF
        with open(real_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Parse it
        document = parser.parse(pdf_bytes, real_pdf_path.name)
        
        # Verify we got text
        assert len(document.text) > 0
        assert document.metadata['num_pages'] > 0
