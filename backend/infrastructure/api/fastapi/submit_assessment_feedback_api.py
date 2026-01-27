from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from application.use_cases.submit_assessment_feedback import SubmitAssessmentFeedbackUseCase
from application.dto.feedback import SubmitAssessmentFeedbackDTO, AssessmentID
from domain.entities.question import QuestionID
from domain.entities.learning import LearningPlanID, StudySessionID


class AssessmentFeedbackRequest(BaseModel):
    """Request model for assessment feedback."""
    agrees: bool
    comment: Optional[str] = None


class SubmitAssessmentFeedbackAPIBase(ABC):
    """Abstract base class for submit assessment feedback endpoints."""

    @abstractmethod
    async def submit_assessment_feedback(
        self,
        learning_plan_id: str,
        session_id: str,
        question_id: str,
        request: AssessmentFeedbackRequest,
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
        request: AssessmentFeedbackRequest,
    ) -> dict:
        """Submit feedback endpoint implementation."""
        # FIXME: I think this is badly modelled, if there is an assessment entity already
        # why not referencing it directly?
        # Generate a unique assessment_id from question context
        # Since there's one assessment per question per session
        assessment_id = f"{session_id}:{question_id}"

        dto = SubmitAssessmentFeedbackDTO(
            assessment_id=AssessmentID(assessment_id),
            question_id=QuestionID(question_id),
            learning_plan_id=LearningPlanID(learning_plan_id),
            session_id=StudySessionID(session_id),
            agrees=request.agrees,
            comment=request.comment,
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
