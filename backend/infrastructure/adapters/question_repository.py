from dataclasses import dataclass
from typing import Dict, Optional, List

from domain.entities.question import Question
from domain.ports.question_repository import QuestionRepository


@dataclass
class InMemoryQuestionRepository(QuestionRepository):
    """
    In-memory implementation of QuestionRepository.

    Stores Question entities in a dictionary keyed by question ID.
    Intended for testing and local development.
    """
    _questions : Dict[str, Question]

    def save(self, question: Question) -> None:
        """
        Persist a Question entity.
        """
        self._questions[question.id] = question

    def get_by_id(self, question_id: str) -> Optional[Question]:
        """
        Retrieve a Question by its ID.
        """
        return self._questions.get(question_id)

    def list_all(self) -> List[Question]:
        """
        List all Question entities.
        """
        return list(self._questions.values())
