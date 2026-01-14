
from typing import NewType, Optional, Any
from dataclasses import dataclass


# Type aliases for clarity
DocumentID = NewType("DocumentID", str)
DocLocation = NewType("DocLocation", str)


@dataclass
class Document:
    id: DocumentID
    text: str
    metadata: Optional[dict] = None  # e.g., title, author, date
    layout: Optional[Any] = None  # optional layout info, paragraphs, etc.
