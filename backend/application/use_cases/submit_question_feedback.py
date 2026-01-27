from dataclasses import dataclass
import logging
from uuid import uuid4

from application.dto.feedback import SubmitQuestionFeedbackDTO
from domain.ports.feedback_service import QuestionFeedbackService
from domain.entities.question import QuestionFeedback, QuestionID, FeedbackID
from domain.entities.learning import LearningPlanID, StudySessionID


@dataclass
class SubmitQuestionFeedbackUseCase:
    """
    Use case for submitting user feedback on question quality.
    
    This allows users to rate the quality and helpfulness of questions,
    which can be used to improve the question generation process.
    """

    feedback_service: QuestionFeedbackService

    def execute(
        self,
        question_feedback_dto: SubmitQuestionFeedbackDTO,
    ) -> QuestionFeedback:
        """
        Submit user feedback for a question's quality.

        Parameters
        ----------
        question_feedback_dto : SubmitQuestionFeedbackDTO
            The DTO containing feedback details.

        Returns
        -------
        QuestionFeedback
            The created feedback object.
        """

        question_id: QuestionID = question_feedback_dto.question_id
        learning_plan_id: LearningPlanID = question_feedback_dto.learning_plan_id
        session_id: StudySessionID = question_feedback_dto.session_id
        is_helpful: bool = question_feedback_dto.is_helpful

        logging.info(
            f"[SubmitQuestionFeedbackUseCase] Submitting feedback for question {question_id} "
            f"in session {session_id}, learning plan {learning_plan_id}"
        )

        # Create feedback entity
        feedback = QuestionFeedback(
            id=FeedbackID(str(uuid4())),
            question_id=question_id,
            learning_plan_id=learning_plan_id,
            session_id=session_id,
            is_helpful=is_helpful,
        )

        # Submit through feedback service
        self.feedback_service.submit_feedback(feedback)

        logging.info(
            f"[SubmitQuestionFeedbackUseCase] Feedback submitted successfully: {feedback.id}"
        )

        return feedback
