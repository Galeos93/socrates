from datetime import datetime, UTC
from typing import  NewType, Optional, List
from dataclasses import dataclass, field


from domain.entities.knowledge_unit import KnowledgeUnitID


QuestionID = NewType("QuestionID", str)
Answer = NewType("Answer", str)


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
    text : str
        The text of the question.
    difficulty : Difficulty
        Difficulty level of the question.
    correct_answer : Answer
        The correct answer to the question.
    attempts : List[AnswerAttempt], optional
        A list of answer attempts made by users. Default is an empty list.
    knowledge_unit : KnowledgeUnit
        The associated knowledge unit (FactKnowledge or SkillKnowledge).
    times_asked : int, optional
        Number of times the question has been asked. Default is 0.
    times_answered_correctly : int, optional
        Number of times the question has been answered correctly. Default is 0.
    """
    id: QuestionID
    text: str
    difficulty: Difficulty
    correct_answer: Answer
    attempts: List[AnswerAttempt] = field(default_factory=list)
    knowledge_unit_id: KnowledgeUnitID
    times_asked: int = 0
    times_answered_correctly: int = 0
    last_time_asked: Optional[str] = None  # ISO formatted datetime string
