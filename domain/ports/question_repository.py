from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities.question import Question


class QuestionRepository(ABC):
    """Repository interface for managing Question entities."""

    @abstractmethod
    def save(self, question: Question) -> None:
        """
        Persist a Question entity.

        Parameters
        ----------
        question : Question
            The Question entity to be saved.
        """
        pass

    @abstractmethod
    def get_by_id(self, question_id: str) -> Optional[Question]:
        """
        Retrieve a Question by its ID.

        Parameters
        ----------
        question_id : str
            The unique identifier of the Question.

        Returns
        -------
        Optional[Question]
            The Question entity if found, otherwise None.
        """
        pass

    @abstractmethod
    def list_all(self) -> List[Question]:
        """
        List all Question entities.

        Returns
        -------
        List[Question]
            A list of all Question entities.
        """
        pass