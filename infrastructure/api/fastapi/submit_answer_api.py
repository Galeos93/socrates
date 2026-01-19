from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.use_cases.submit_answer import SubmitAnswerUseCase


class SubmitAnswerAPIBase(ABC):
    """Abstract base class for submitting answer endpoints."""

    @abstractmethod
    async def submit_answer(
        self, 
        learning_plan_id: str, 
        session_id: str, 
        question_id: str
    ) -> dict:
        """Submit an answer to a question."""
        pass


@dataclass
class SubmitAnswerAPIImpl(SubmitAnswerAPIBase):
    """Implementation of the SubmitAnswerAPIBase."""
    submit_answer_use_case: SubmitAnswerUseCase

    async def submit_answer(
        self, 
        learning_plan_id: str, 
        session_id: str, 
        question_id: str
    ) -> dict:
        """Submit answer endpoint implementation."""
        self.submit_answer_use_case.execute(
            learning_plan_id=learning_plan_id,
            study_session_id=session_id,
            question_id=question_id,
        )
        
        return {"status": "answer_submitted"}
