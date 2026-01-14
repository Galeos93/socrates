from abc import ABC, abstractmethod
from typing import List

from domain.entities.knowledge_unit import KnowledgeUnit
from domain.entities.question import Question


class MasteryService(ABC):
    @abstractmethod
    def update_mastery(
        self,
        ku: KnowledgeUnit,
        questions: List[Question]
    ) -> KnowledgeUnit:
        """
        Update the mastery level of a KnowledgeUnit based on question performance.

        Parameters
        ----------
        ku: KnowledgeUnit
            The fact or skill to update mastery for.
        questions: List[Question]
            List of questions answered related to the KnowledgeUnit.

        Returns
        -------
        KnowledgeUnit

        """
        pass


class QuestionBasedMasteryService(MasteryService):

    @staticmethod
    def compute_mastery_from_questions(questions: List[Question]) -> float:
        if not questions:
            return 0.0

        total = 0.0
        weight_sum = 0.0

        for q in questions:
            if q.times_asked == 0:
                continue

            accuracy = q.times_answered_correctly / q.times_asked
            weight = q.difficulty.level

            total += accuracy * weight
            weight_sum += weight

        return min(1.0, total / weight_sum) if weight_sum > 0 else 0.0

    def calculate_mastery_from_questions(
        self,
        ku: KnowledgeUnit,
        questions: List[Question]
    ) -> float:
        """
        Calculate mastery level from question performance.

        Parameters
        ----------
        ku: KnowledgeUnit
            The fact or skill to calculate mastery for.
        questions: List[Question]
            List of questions answered related to the KnowledgeUnit.

        Returns
        -------
        float
            New mastery level between 0.0 and 1.0.
        """
        return self.compute_mastery_from_questions(questions)
