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
