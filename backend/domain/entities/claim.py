from typing import Optional
from dataclasses import dataclass

from domain.entities.document import DocumentID, DocLocation


@dataclass
class Claim:
    """A discrete piece of knowledge extracted from a text that can be directly
    or indirectly verified using the text itself."""
    text: str
    doc_id: DocumentID
    doc_location: Optional[DocLocation] = None  # e.g., character range or paragraph ID

