from abc import ABC, abstractmethod
from typing import List

from domain.entities.knowledge_unit import KnowledgeUnit
from domain.entities.question import SessionQuestion


class MasteryService(ABC):
    @abstractmethod
    def update_mastery(
        self,
        ku: KnowledgeUnit,
        session_questions: List[SessionQuestion],
    ) -> KnowledgeUnit:
        """
        Update the mastery level of a KnowledgeUnit based on session question outcomes.

        Parameters
        ----------
        ku: KnowledgeUnit
            The knowledge unit to update.
        session_questions: List[SessionQuestion]
            Session-specific question outcomes related to this KnowledgeUnit.

        Returns
        -------
        KnowledgeUnit
            The updated KnowledgeUnit.
        """
        pass


class QuestionBasedMasteryService(MasteryService):
    """Computes mastery based on session-level question outcomes.

    Notes
    -----

    Rules:
    - Correct answers increase mastery
    - Incorrect answers decrease mastery
    - Multiple attempts penalize mastery

    """
    def update_mastery(
        self,
        ku: KnowledgeUnit,
        session_questions: List[SessionQuestion],
    ) -> KnowledgeUnit:
        ku.mastery_level = self.compute_mastery(session_questions)
        return ku

    @staticmethod
    def compute_mastery(
        session_questions: List[SessionQuestion],
    ) -> float:
        if not session_questions:
            return 0.0

        score = 0.0
        max_score = 0.0

        for sq in session_questions:
            if sq.is_correct is None:
                continue

            # Base score per question
            max_score += 1.0

            if sq.is_correct:
                # Penalize retries
                penalty = max(0.0, 1.0 - 0.2 * (sq.attempts - 1))
                score += penalty
            else:
                score += 0.0

        if max_score == 0:
            return 0.0

        return min(1.0, score / max_score)