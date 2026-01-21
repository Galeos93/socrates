from abc import ABC, abstractmethod
from typing import List

from domain.entities.knowledge_unit import KnowledgeUnit
from domain.entities.question import SessionQuestion, AnswerAssessment


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
    """
    Computes mastery based on session-level question outcomes.

    Rules
    -----
    - Only assessed attempts are considered
    - Latest assessed attempt determines correctness
    - Multiple attempts reduce score
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

        total_score = 0.0
        max_score = 0.0

        for sq in session_questions:
            assessed_attempts = [
                a for a in sq.attempts if a.assessment is not None
            ]

            if not assessed_attempts:
                continue  # unanswered → no contribution

            latest_attempt = assessed_attempts[-1]
            assessment: AnswerAssessment = latest_attempt.assessment

            max_score += 1.0

            if assessment.is_correct:
                attempts_count = len(assessed_attempts)
                penalty = max(0.0, 1.0 - 0.2 * (attempts_count - 1))
                total_score += penalty
            else:
                total_score += 0.0

        if max_score == 0.0:
            return 0.0

        return min(1.0, total_score / max_score)
