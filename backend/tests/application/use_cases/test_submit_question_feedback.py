"""Integration test for question feedback submission flow."""
from unittest.mock import Mock

from domain.entities.question import QuestionFeedback, QuestionID, FeedbackID
from domain.entities.learning import LearningPlanID, StudySessionID
from application.use_cases.submit_question_feedback import SubmitQuestionFeedbackUseCase
from application.dto.feedback import SubmitQuestionFeedbackDTO
from domain.ports.feedback_service import QuestionFeedbackService


class TestSubmitQuestionFeedbackUseCase:
    """Test cases for SubmitQuestionFeedbackUseCase."""

    @staticmethod
    def test_execute_creates_feedback_helpful():
        """Test that feedback is created when question is helpful."""
        # Arrange
        mock_feedback_service = Mock(spec=QuestionFeedbackService)
        use_case = SubmitQuestionFeedbackUseCase(feedback_service=mock_feedback_service)
        
        learning_plan_id = LearningPlanID("lp-123")
        session_id = StudySessionID("session-456")
        question_id = QuestionID("q-789")
        is_helpful = True
        
        dto = SubmitQuestionFeedbackDTO(
            question_id=question_id,
            learning_plan_id=learning_plan_id,
            session_id=session_id,
            is_helpful=is_helpful,
        )
        
        # Act
        feedback = use_case.execute(question_feedback_dto=dto)
        
        # Assert
        assert feedback.learning_plan_id == learning_plan_id
        assert feedback.session_id == session_id
        assert feedback.question_id == question_id
        assert feedback.is_helpful is True
        assert feedback.id is not None
        mock_feedback_service.submit_feedback.assert_called_once_with(feedback)

    @staticmethod
    def test_execute_creates_feedback_not_helpful():
        """Test that feedback is created when question is not helpful."""
        # Arrange
        mock_feedback_service = Mock(spec=QuestionFeedbackService)
        use_case = SubmitQuestionFeedbackUseCase(feedback_service=mock_feedback_service)
        
        dto = SubmitQuestionFeedbackDTO(
            question_id=QuestionID("q-789"),
            learning_plan_id=LearningPlanID("lp-123"),
            session_id=StudySessionID("session-456"),
            is_helpful=False,
        )
        
        # Act
        feedback = use_case.execute(question_feedback_dto=dto)
        
        # Assert
        assert feedback.is_helpful is False
        mock_feedback_service.submit_feedback.assert_called_once()
