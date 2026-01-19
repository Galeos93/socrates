from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.use_cases.assess_question import AssessQuestionOutcomeUseCase
from domain.entities.question import Answer


class AssessQuestionAPIBase(ABC):
    """Abstract base class for assessing question endpoints."""

    @abstractmethod
    async def assess_question(
        self,
        learning_plan_id: str,
        session_id: str,
        question_id: str,
        user_answer: str,
    ) -> dict:
        """Assess a question answer."""
        pass


@dataclass
class AssessQuestionAPIImpl(AssessQuestionAPIBase):
    """Implementation of the AssessQuestionAPIBase."""
    assess_question_use_case: AssessQuestionOutcomeUseCase

    async def assess_question(
        self,
        learning_plan_id: str,
        session_id: str,
        question_id: str,
        user_answer: str,
    ) -> dict:
        """Assess question endpoint implementation."""
        is_correct = self.assess_question_use_case.execute(
            learning_plan_id=learning_plan_id,
            study_session_id=session_id,
            question_id=question_id,
            user_answer=Answer(user_answer),
        )
        
        return {
            "is_correct": is_correct,
            "question_id": question_id,
        }
