import dataclass
from enum import Enum

from domain.entities.question import QuestionStatus


@dataclass(frozen=True)
class QuestionView:
    id: str
    text: str
    status: QuestionStatus
    attempts: int
