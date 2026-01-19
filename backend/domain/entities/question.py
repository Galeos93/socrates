from datetime import datetime, UTC
from enum import Enum
from typing import  NewType, Optional, List
from dataclasses import dataclass, field


from domain.entities.knowledge_unit import KnowledgeUnitID


QuestionID = NewType("QuestionID", str)
Answer = NewType("Answer", str)


class QuestionStatus(str, Enum):
    PENDING = "pending"
    CORRECT = "correct"
    INCORRECT = "incorrect"


@dataclass
class Difficulty:
    """Represents the difficulty level of a question."""
    level: int  # e.g., 1 to 5
    description: Optional[str] = ""


@dataclass(frozen=True)
class AnswerAttempt:
    user_answer: Answer
    is_correct: bool | None = None
    answered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    score: float | None = None  # optional for partial credit


@dataclass
class Question:
    """
    A question designed to test fact comprehension or skill application.

    Attributes
    ----------
    id : QuestionID
        Unique identifier for the question.
    text : str
        The text of the question.
    difficulty : Difficulty
        Difficulty level of the question.
    correct_answer : Answer
        The correct answer to the question.
    knowledge_unit : KnowledgeUnit
        The associated knowledge unit (FactKnowledge or SkillKnowledge).
    """
    id: QuestionID
    text: str
    difficulty: Difficulty
    correct_answer: Answer
    knowledge_unit_id: KnowledgeUnitID


@dataclass
class SessionQuestion:
    """
    A Question as it appears within a specific StudySession.
    Holds session-specific state.
    """
    question_id: QuestionID
    attempts: int = 0
    is_correct: bool | None = None  # None = unanswered
    last_answered_at: datetime | None = None
    knowledge_unit_id: KnowledgeUnitID | None = None

    def register_attempt(self) -> None:
        if self.is_correct is not None:
            raise ValueError("Question already assessed")

        self.attempts += 1
        self.last_answered_at = datetime.now(UTC)

    def mark_correctness(self, correct: bool) -> None:
        if self.attempts == 0:
            raise ValueError("Cannot assess without an attempt")

        if self.is_correct is not None:
            raise ValueError("Correctness already assigned")

        self.is_correct = correct

    @property
    def status(self) -> str:
        if self.is_correct is None:
            return QuestionStatus.PENDING.value
        elif self.is_correct:
            return QuestionStatus.CORRECT.value
        else:
            return QuestionStatus.INCORRECT.value
