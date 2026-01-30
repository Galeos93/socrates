from abc import ABC, abstractmethod

from domain.entities.knowledge_unit import KnowledgeUnit
from domain.entities.question import Question


class QuestionGenerationService(ABC):
    @abstractmethod
    def generate_next_question(
        self,
        ku: KnowledgeUnit
    ) -> Question:
        """Generate a question for a KnowledgeUnit.

        Parameters
        ----------
        ku: KnowledgeUnit
            The fact or skill to generate a question for.

        Returns
        -------
        Question
        """
        pass

    @abstractmethod
    def generate_questions_batch(
        self,
        ku: KnowledgeUnit,
        max_count: int
    ) -> list[Question]:
        """Generate multiple diverse questions for a KnowledgeUnit.

        Parameters
        ----------
        ku: KnowledgeUnit
            The fact or skill to generate questions for.
        max_count: int
            Max number of questions to generate.

        Returns
        -------
        list[Question]
            A list of diverse questions for the knowledge unit.
        """
        pass
