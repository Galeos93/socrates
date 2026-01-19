from dataclasses import dataclass
from typing import List

from domain.entities.document import DocumentID


@dataclass
class CreateLearningPlanRequest:
    """Request model for creating a learning plan."""
    document_ids: List[DocumentID]
