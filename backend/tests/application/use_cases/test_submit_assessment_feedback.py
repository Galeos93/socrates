"""Integration test for assessment feedback submission flow."""
import pytest
from unittest.mock import Mock
from domain.entities.question import AssessmentFeedback, QuestionID, FeedbackID
from domain.entities.learning import LearningPlanID, StudySessionID
from application.use_cases.submit_assessment_feedback import SubmitAssessmentFeedbackUseCase
from application.dto.feedback import SubmitAssessmentFeedbackDTO, AssessmentID
from domain.ports.feedback_service import AssessmentFeedbackService


class TestSubmitAssessmentFeedbackUseCase:
    """Test cases for SubmitAssessmentFeedbackUseCase."""

    @staticmethod
    def test_execute_creates_feedback_with_valid_score():
        """Test that feedback is created with valid score."""
        # Arrange
        mock_feedback_service = Mock(spec=AssessmentFeedbackService)
        use_case = SubmitAssessmentFeedbackUseCase(feedback_service=mock_feedback_service)
        
        learning_plan_id = LearningPlanID("lp-123")
        session_id = StudySessionID("session-456")
        question_id = QuestionID("q-789")
        assessment_id = AssessmentID("assessment-001")
        agrees = True
        comment = "Great question!"
        
        dto = SubmitAssessmentFeedbackDTO(
            assessment_id=assessment_id,
            question_id=question_id,
            learning_plan_id=learning_plan_id,
            session_id=session_id,
            agrees=agrees,
            comment=comment,
        )
        
        # Act
        feedback = use_case.execute(assessment_feedback_dto=dto)
        
        # Assert
        assert feedback.learning_plan_id == learning_plan_id
        assert feedback.session_id == session_id
        assert feedback.question_id == question_id
        assert feedback.score == 5  # agrees=True maps to score 5
        assert feedback.comment == comment
        assert feedback.id is not None
        mock_feedback_service.submit_feedback.assert_called_once_with(feedback)

    @staticmethod
    def test_execute_disagrees_maps_to_low_score():
        """Test that agrees=False maps to score 1."""
        # Arrange
        mock_feedback_service = Mock(spec=AssessmentFeedbackService)
        use_case = SubmitAssessmentFeedbackUseCase(feedback_service=mock_feedback_service)
        
        dto = SubmitAssessmentFeedbackDTO(
            assessment_id=AssessmentID("assessment-001"),
            question_id=QuestionID("q-789"),
            learning_plan_id=LearningPlanID("lp-123"),
            session_id=StudySessionID("session-456"),
            agrees=False,
        )
        
        # Act
        feedback = use_case.execute(assessment_feedback_dto=dto)
        
        # Assert
        assert feedback.score == 1  # agrees=False maps to score 1
        mock_feedback_service.submit_feedback.assert_called_once()

    @staticmethod
    def test_execute_allows_optional_comment():
        """Test that comment is optional."""
        # Arrange
        mock_feedback_service = Mock(spec=AssessmentFeedbackService)
        use_case = SubmitAssessmentFeedbackUseCase(feedback_service=mock_feedback_service)
        
        dto = SubmitAssessmentFeedbackDTO(
            assessment_id=AssessmentID("assessment-001"),
            question_id=QuestionID("q-789"),
            learning_plan_id=LearningPlanID("lp-123"),
            session_id=StudySessionID("session-456"),
            agrees=True,
            comment=None,
        )
        
        # Act
        feedback = use_case.execute(assessment_feedback_dto=dto)
        
        # Assert
        assert feedback.comment is None
        mock_feedback_service.submit_feedback.assert_called_once()
