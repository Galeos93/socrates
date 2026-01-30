import base64
import io
import uuid
from pathlib import Path
from typing import List

import pymupdf
from PIL import Image

from domain.entities.document import Document, DocumentID
from domain.ports.document_parser import DocumentParser


class LLMOCRDocumentParser(DocumentParser):
    """
    LLM-based OCR document parser that uses OpenAI's vision API to extract text from PDFs.

    Converts PDF pages to images and sends them to the LLM for text extraction.
    Currently only supports PDF files.
    """

    def __init__(self, client, model: str = "gpt-4o"):
        """
        Initialize the LLM OCR parser.

        Parameters
        ----------
        client
            OpenAI client instance for making API calls.
        model : str
            OpenAI model to use for vision tasks (default: "gpt-4o").
        """
        self.client = client
        self.model = model
        self.max_tokens_per_page = 1500
        self.dpi = 150  # DPI for image conversion

    def parse(self, file_bytes: bytes, filename: str) -> Document:
        """
        Parse PDF bytes into a Document entity using LLM-based OCR.

        Parameters
        ----------
        file_bytes : bytes
            Raw bytes of the PDF file.
        filename : str
            Original filename including extension.

        Returns
        -------
        Document
            Document entity with extracted text content.

        Raises
        ------
        ValueError
            If the file format is not PDF.
        """
        # Validate file format
        file_extension = Path(filename).suffix.lower()
        if file_extension != ".pdf":
            raise ValueError(f"Unsupported file format: {file_extension}. Only PDF files are supported.")

        # Convert PDF pages to images
        images = self._pdf_to_images(file_bytes)

        # Extract text from each page using LLM
        page_texts: List[str] = []
        for page_num, image in enumerate(images, start=1):
            text = self._extract_text_from_image(image, page_num)
            page_texts.append(text)

        # Combine all pages
        full_text = "\n\n".join(page_texts)

        # Create Document entity
        document_id = DocumentID(str(uuid.uuid4()))
        document = Document(
            id=document_id,
            text=full_text,
            metadata={
                "filename": filename,
                "num_pages": len(images),
                "parser": "llm_ocr"
            }
        )

        return document

    def _pdf_to_images(self, pdf_bytes: bytes) -> List[Image.Image]:
        """
        Convert PDF bytes to a list of PIL images using PyMuPDF.

        Parameters
        ----------
        pdf_bytes : bytes
            Raw PDF file bytes.

        Returns
        -------
        List[Image.Image]
            List of PIL images, one per page.
        """
        # Open PDF from bytes
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

        images = []
        zoom = self.dpi / 72  # DPI is usually enough for OCR
        mat = pymupdf.Matrix(zoom, zoom)

        for page in doc:
            pix = page.get_pixmap(matrix=mat, colorspace=pymupdf.csGRAY)
            img = Image.frombytes("L", [pix.width, pix.height], pix.samples)
            images.append(img)

        doc.close()
        return images

    def _extract_text_from_image(self, image: Image.Image, page_num: int) -> str:
        """
        Extract text from a single image using OpenAI's vision API.

        Parameters
        ----------
        image : Image.Image
            PIL image of the page.
        page_num : int
            Page number for context.

        Returns
        -------
        str
            Extracted text from the image.
        """
        # Convert PIL image to base64
        base64_image = self._image_to_base64(image)

        # Create prompt for LLM
        prompt = (
            "Extract all text from this document page. "
            "Preserve the structure and formatting as much as possible. "
            "Include headings, paragraphs, lists, and any other text content. "
            "Do not add any commentary or explanation - only return the extracted text."
        )

        # Call OpenAI vision API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=self.max_tokens_per_page
        )

        # Extract text from response
        extracted_text = response.choices[0].message.content
        return extracted_text.strip() if extracted_text else ""

    def _image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL image to base64 string.

        Parameters
        ----------
        image : Image.Image
            PIL image to convert.

        Returns
        -------
        str
            Base64 encoded image string.
        """
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=70, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode()
