from dataclasses import dataclass
import logging
from uuid import uuid4

from application.dto.feedback import SubmitAssessmentFeedbackDTO
from domain.ports.feedback_service import AssessmentFeedbackService
from domain.entities.question import AssessmentFeedback, QuestionID, FeedbackID
from domain.entities.learning import LearningPlanID, StudySessionID


@dataclass
class SubmitAssessmentFeedbackUseCase:
    """
    Use case for submitting user feedback on question assessments.
    
    This allows users to rate and comment on the quality of assessments,
    which can be used to improve the question generation and evaluation process.
    """

    feedback_service: AssessmentFeedbackService

    def execute(
        self,
        assessment_feedback_dto: SubmitAssessmentFeedbackDTO,
    ) -> AssessmentFeedback:
        """
        Submit user feedback for a question assessment.

        Parameters
        ----------
        assessment_feedback_dto : SubmitAssessmentFeedbackDTO
            The DTO containing feedback details.

        Returns
        -------
        AssessmentFeedback
            The created feedback object.
        """

        question_id: QuestionID = assessment_feedback_dto.question_id
        learning_plan_id: LearningPlanID = assessment_feedback_dto.learning_plan_id
        session_id: StudySessionID = assessment_feedback_dto.session_id
        score: int = 5 if assessment_feedback_dto.agrees else 1
        comment: str | None = assessment_feedback_dto.comment

        logging.info(
            f"[SubmitAssessmentFeedbackUseCase] Submitting feedback for question {question_id} "
            f"in session {session_id}, learning plan {learning_plan_id}"
        )

        # Create feedback entity
        feedback = AssessmentFeedback(
            id=FeedbackID(str(uuid4())),
            question_id=question_id,
            learning_plan_id=learning_plan_id,
            session_id=session_id,
            score=score,
            comment=comment,
        )

        # Submit through feedback service
        self.feedback_service.submit_feedback(feedback)

        logging.info(
            f"[SubmitAssessmentFeedbackUseCase] Feedback submitted successfully: {feedback.id}"
        )

        return feedback
