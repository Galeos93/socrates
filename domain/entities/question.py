from typing import  NewType, Optional
from dataclasses import dataclass


from domain.entities.knowledge_unit import KnowledgeUnit


Answer = NewType("Answer", str)


@dataclass
class Difficulty:
    """Represents the difficulty level of a question."""
    level: int  # e.g., 1 to 5
    description: Optional[str] = ""


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
    answer : Answer
        Correct answer.
    knowledge_unit : KnowledgeUnit
        The associated knowledge unit (FactKnowledge or SkillKnowledge).
    times_asked : int, optional
        Number of times the question has been asked. Default is 0.
    times_answered_correctly : int, optional
        Number of times the question has been answered correctly. Default is 0.
    """
    text: str
    difficulty: Difficulty
    answer: Answer
    knowledge_unit: KnowledgeUnit
    times_asked: int = 0
    times_answered_correctly: int = 0
    last_time_asked: Optional[str] = None  # ISO formatted datetime string
