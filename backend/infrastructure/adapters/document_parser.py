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
    Pages are processed in batches to minimize the number of OpenAI calls and
    reduce overall latency.

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
        self.batch_size = 4  # Number of pages per OpenAI request

    def parse(self, file_bytes: bytes, filename: str) -> Document:
        """
        Parse PDF bytes into a Document entity using LLM-based OCR.

        The PDF is rendered to images, which are then processed in batches.
        Each batch is sent as a single OpenAI vision request to amortize
        model and network overhead.

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
        RuntimeError
            If the number of extracted pages does not match the input pages.
        """
        file_extension = Path(filename).suffix.lower()
        if file_extension != ".pdf":
            raise ValueError(
                f"Unsupported file format: {file_extension}. Only PDF files are supported."
            )

        images = self._pdf_to_images(file_bytes)

        page_texts: List[str] = []

        for i in range(0, len(images), self.batch_size):
            batch = images[i:i + self.batch_size]
            batch_texts = self._extract_text_from_images_batch(
                batch,
                start_page=i + 1
            )
            page_texts.extend(batch_texts)

        full_text = "\n\n".join(page_texts)

        document_id = DocumentID(str(uuid.uuid4()))
        return Document(
            id=document_id,
            text=full_text,
            metadata={
                "filename": filename,
                "num_pages": len(images),
                "parser": "llm_ocr_batched"
            }
        )

    def _pdf_to_images(self, pdf_bytes: bytes) -> List[Image.Image]:
        """
        Convert PDF bytes to a list of PIL images using PyMuPDF.

        Pages are rendered at the configured DPI and converted to grayscale
        images to reduce payload size while preserving OCR quality.

        Parameters
        ----------
        pdf_bytes : bytes
            Raw PDF file bytes.

        Returns
        -------
        List[Image.Image]
            List of PIL images, one per page.
        """
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

        images = []
        zoom = self.dpi / 72
        mat = pymupdf.Matrix(zoom, zoom)

        for page in doc:
            pix = page.get_pixmap(matrix=mat, colorspace=pymupdf.csGRAY)
            img = Image.frombytes("L", [pix.width, pix.height], pix.samples)
            images.append(img)

        doc.close()
        return images

    def _extract_text_from_images_batch(
        self,
        images: List[Image.Image],
        start_page: int
    ) -> List[str]:
        """
        Extract text from multiple page images using a single OpenAI vision request.

        The model is instructed to return text for each page in order, separated
        by a deterministic page-break marker. The output is split back into
        per-page text segments.

        Parameters
        ----------
        images : List[Image.Image]
            List of PIL images representing consecutive document pages.
        start_page : int
            Page number of the first image in the batch (used for context/debugging).

        Returns
        -------
        List[str]
            Extracted text for each page in the batch, in order.

        Raises
        ------
        RuntimeError
            If the number of returned page segments does not match the input.
        """
        images_b64 = [self._image_to_base64(img) for img in images]

        prompt = (
            "You will receive multiple document page images.\n"
            "Extract all text from EACH page.\n\n"
            "Rules:\n"
            "- Preserve structure and formatting\n"
            "- Do NOT add commentary or explanations\n"
            "- Return pages IN ORDER\n"
            "- Separate pages with this exact marker:\n"
            "=== PAGE BREAK ===\n"
        )

        content = [{"type": "text", "text": prompt}]
        content.extend(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"
                }
            }
            for img_b64 in images_b64
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            max_tokens=len(images) * self.max_tokens_per_page
        )

        text = response.choices[0].message.content or ""
        pages = [p.strip() for p in text.split("=== PAGE BREAK ===")]

        if len(pages) != len(images):
            raise RuntimeError(
                f"OCR page count mismatch starting at page {start_page}: "
                f"expected {len(images)}, got {len(pages)}"
            )

        return pages

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
            Base64-encoded JPEG image string.
        """
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=70, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode()
