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
    answered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    assessment: "AnswerAssessment | None" = None


@dataclass(frozen=True)
class AnswerAssessment:
    is_correct: bool
    correct_answer: Answer | None = None
    explanation: str | None = None
    confidence: float | None = None
    assessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


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
    attempts: list[AnswerAttempt] = field(default_factory=list)
    last_answered_at: datetime | None = None
    knowledge_unit_id: KnowledgeUnitID | None = None

    def submit_answer(self, user_answer: Answer) -> None:
        self.attempts.append(
            AnswerAttempt(
                user_answer=user_answer,
                answered_at=datetime.now(UTC),
            )
        )
        self.last_answered_at = datetime.now(UTC)


    def latest_unassessed_attempt(self) -> AnswerAttempt | None:
        for attempt in reversed(self.attempts):
            if attempt.assessment is None:
                return attempt
        return None


    def attach_assessment(
        self,
        attempt: AnswerAttempt,
        assessment: AnswerAssessment
    ) -> None:
        index = self.attempts.index(attempt)
        self.attempts[index] = AnswerAttempt(
            user_answer=attempt.user_answer,
            answered_at=attempt.answered_at,
            assessment=assessment,
        )

    @property
    def status(self) -> QuestionStatus:
        if not self.attempts:
            return QuestionStatus.PENDING

        # Use last assessed attempt
        for attempt in reversed(self.attempts):
            if attempt.assessment is not None:
                return (
                    QuestionStatus.CORRECT
                    if attempt.assessment.is_correct
                    else QuestionStatus.INCORRECT
                )

        return QuestionStatus.PENDING
