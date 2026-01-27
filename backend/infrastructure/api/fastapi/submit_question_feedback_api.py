from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.use_cases.submit_question_feedback import SubmitQuestionFeedbackUseCase
from application.dto.feedback import SubmitQuestionFeedbackDTO
from domain.entities.question import QuestionID
from domain.entities.learning import LearningPlanID, StudySessionID


class SubmitQuestionFeedbackAPIBase(ABC):
    """Abstract base class for submit question feedback endpoints."""

    @abstractmethod
    async def submit_question_feedback(
        self,
        learning_plan_id: str,
        session_id: str,
        question_id: str,
        is_helpful: bool,
    ) -> dict:
        """Submit user feedback for a question's quality."""
        pass


@dataclass
class SubmitQuestionFeedbackAPIImpl(SubmitQuestionFeedbackAPIBase):
    """Implementation of the SubmitQuestionFeedbackAPIBase."""

    submit_question_feedback_use_case: SubmitQuestionFeedbackUseCase

    async def submit_question_feedback(
        self,
        learning_plan_id: str,
        session_id: str,
        question_id: str,
        is_helpful: bool,
    ) -> dict:
        """Submit question feedback endpoint implementation."""
        dto = SubmitQuestionFeedbackDTO(
            question_id=QuestionID(question_id),
            learning_plan_id=LearningPlanID(learning_plan_id),
            session_id=StudySessionID(session_id),
            is_helpful=is_helpful,
        )
        
        feedback = self.submit_question_feedback_use_case.execute(
            question_feedback_dto=dto
        )

        return {
            "feedback_id": feedback.id,
            "question_id": feedback.question_id,
            "is_helpful": feedback.is_helpful,
            "message": "Question feedback submitted successfully",
        }
