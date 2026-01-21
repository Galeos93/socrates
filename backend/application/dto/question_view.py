from dataclasses import dataclass
from enum import Enum

from domain.entities.question import QuestionStatus, QuestionID
from domain.entities.knowledge_unit import KnowledgeUnitID


@dataclass(frozen=True)
class QuestionView:
    id: QuestionID
    knowledge_unit_id: KnowledgeUnitID
    text: str
    status: QuestionStatus
    attempts: int
