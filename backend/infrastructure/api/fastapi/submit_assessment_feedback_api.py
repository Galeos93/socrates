from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.use_cases.submit_assessment_feedback import SubmitAssessmentFeedbackUseCase
from application.dto.feedback import SubmitAssessmentFeedbackDTO, AssessmentID
from domain.entities.question import QuestionID
from domain.entities.learning import LearningPlanID, StudySessionID


class SubmitAssessmentFeedbackAPIBase(ABC):
    """Abstract base class for submit assessment feedback endpoints."""

    @abstractmethod
    async def submit_assessment_feedback(
        self,
        learning_plan_id: str,
        session_id: str,
        question_id: str,
        assessment_id: str,
        agrees: bool,
        comment: str | None = None,
    ) -> dict:
        """Submit user feedback for a question assessment."""
        pass


@dataclass
class SubmitAssessmentFeedbackAPIImpl(SubmitAssessmentFeedbackAPIBase):
    """Implementation of the SubmitAssessmentFeedbackAPIBase."""

    submit_assessment_feedback_use_case: SubmitAssessmentFeedbackUseCase

    async def submit_assessment_feedback(
        self,
        learning_plan_id: str,
        session_id: str,
        question_id: str,
        assessment_id: str,
        agrees: bool,
        comment: str | None = None,
    ) -> dict:
        """Submit feedback endpoint implementation."""
        dto = SubmitAssessmentFeedbackDTO(
            assessment_id=AssessmentID(assessment_id),
            question_id=QuestionID(question_id),
            learning_plan_id=LearningPlanID(learning_plan_id),
            session_id=StudySessionID(session_id),
            agrees=agrees,
            comment=comment,
        )
        
        feedback = self.submit_assessment_feedback_use_case.execute(
            assessment_feedback_dto=dto
        )

        return {
            "feedback_id": feedback.id,
            "question_id": feedback.question_id,
            "score": feedback.score,
            "message": "Assessment feedback submitted successfully",
        }
