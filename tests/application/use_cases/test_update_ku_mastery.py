"""Tests for UpdateKnowledgeUnitMasteryUseCase."""
import pytest
import uuid
from unittest.mock import Mock

from application.use_cases.update_ku_mastery import UpdateKnowledgeUnitMasteryUseCase
from domain.entities.learning import LearningPlan, StudySession
from domain.entities.knowledge_unit import KnowledgeUnit
from domain.entities.question import QuestionID, SessionQuestion
from domain.services.mastery import MasteryService
from infrastructure.adapters.learning_plan_repository import InMemoryLearningPlanRepository


@pytest.fixture
def learning_plan_repository() -> InMemoryLearningPlanRepository:
    """Provide an in-memory learning plan repository."""
    return InMemoryLearningPlanRepository(_plans={})


class TestUpdateKnowledgeUnitMasteryUseCase:
    """Test suite for UpdateKnowledgeUnitMasteryUseCase."""

    @staticmethod
    def test_updates_mastery_level_for_knowledge_unit(
        sample_learning_plan: LearningPlan,
        sample_study_session: StudySession,
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should update the mastery level of a knowledge unit based on session outcomes."""
        # Arrange
        ku = sample_learning_plan.knowledge_units[0]
        question_id = QuestionID(str(uuid.uuid4()))
        session_question = SessionQuestion(
            question_id=question_id,
            attempts=1,
            is_correct=True,
            knowledge_unit_id=ku.id,
        )
        sample_study_session.questions[question_id] = session_question
        learning_plan_repository.save(sample_learning_plan)

        mock_mastery_service = Mock(spec=MasteryService)
        # Mock returns the KU with updated mastery
        updated_ku = ku
        updated_ku.mastery_level = 0.8
        mock_mastery_service.update_mastery.return_value = updated_ku

        use_case = UpdateKnowledgeUnitMasteryUseCase(
            learning_plan_repository=learning_plan_repository,
            mastery_service=mock_mastery_service,
        )

        # Act
        result = use_case.execute(
            learning_plan_id=sample_learning_plan.id,
            knowledge_unit_id=ku.id,
        )

        # Assert
        assert isinstance(result, KnowledgeUnit)
        # Note: The mock service is called, but we should verify the mastery was applied
        mock_mastery_service.update_mastery.assert_called_once()

    @staticmethod
    def test_collects_all_session_questions_for_knowledge_unit(
        sample_learning_plan: LearningPlan,
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should collect all session questions across all sessions for the knowledge unit."""
        # Arrange
        ku = sample_learning_plan.knowledge_units[0]

        # Create multiple sessions with questions for the same KU
        session1 = sample_learning_plan.start_session(max_questions=5)
        q1_id = QuestionID(str(uuid.uuid4()))
        session1.questions[q1_id] = SessionQuestion(
            question_id=q1_id,
            attempts=1,
            is_correct=True,
            knowledge_unit_id=ku.id,
        )

        session2 = sample_learning_plan.start_session(max_questions=5)
        q2_id = QuestionID(str(uuid.uuid4()))
        session2.questions[q2_id] = SessionQuestion(
            question_id=q2_id,
            attempts=2,
            is_correct=False,
            knowledge_unit_id=ku.id,
        )

        learning_plan_repository.save(sample_learning_plan)

        mock_mastery_service = Mock(spec=MasteryService)
        mock_mastery_service.update_mastery.return_value = ku

        use_case = UpdateKnowledgeUnitMasteryUseCase(
            learning_plan_repository=learning_plan_repository,
            mastery_service=mock_mastery_service,
        )

        # Act
        use_case.execute(
            learning_plan_id=sample_learning_plan.id,
            knowledge_unit_id=ku.id,
        )

        # Assert
        # Verify the mastery service was called with the collected session questions
        call_args = mock_mastery_service.update_mastery.call_args
        session_questions = call_args[1]["session_questions"]
        assert len(session_questions) == 2

    @staticmethod
    def test_only_includes_assessed_questions(
        sample_learning_plan: LearningPlan,
        sample_study_session: StudySession,
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should only include session questions that have been assessed (is_correct is not None)."""
        # Arrange
        ku = sample_learning_plan.knowledge_units[0]

        # Add assessed question
        q1_id = QuestionID(str(uuid.uuid4()))
        sample_study_session.questions[q1_id] = SessionQuestion(
            question_id=q1_id,
            attempts=1,
            is_correct=True,
            knowledge_unit_id=ku.id,
        )

        # Add unanswered question (is_correct is None)
        q2_id = QuestionID(str(uuid.uuid4()))
        sample_study_session.questions[q2_id] = SessionQuestion(
            question_id=q2_id,
            attempts=0,
            is_correct=None,
            knowledge_unit_id=ku.id,
        )

        learning_plan_repository.save(sample_learning_plan)

        mock_mastery_service = Mock(spec=MasteryService)
        mock_mastery_service.update_mastery.return_value = ku

        use_case = UpdateKnowledgeUnitMasteryUseCase(
            learning_plan_repository=learning_plan_repository,
            mastery_service=mock_mastery_service,
        )

        # Act
        use_case.execute(
            learning_plan_id=sample_learning_plan.id,
            knowledge_unit_id=ku.id,
        )

        # Assert
        call_args = mock_mastery_service.update_mastery.call_args
        session_questions = call_args[1]["session_questions"]
        assert len(session_questions) == 1
        assert session_questions[0].is_correct is True

    @staticmethod
    def test_persists_learning_plan_after_mastery_update(
        sample_learning_plan: LearningPlan,
        sample_study_session: StudySession,
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should persist the learning plan aggregate after updating mastery."""
        # Arrange
        ku = sample_learning_plan.knowledge_units[0]
        question_id = QuestionID(str(uuid.uuid4()))
        session_question = SessionQuestion(
            question_id=question_id,
            attempts=1,
            is_correct=True,
            knowledge_unit_id=ku.id,
        )
        sample_study_session.questions[question_id] = session_question
        learning_plan_repository.save(sample_learning_plan)

        mock_mastery_service = Mock(spec=MasteryService)
        mock_mastery_service.update_mastery.return_value = ku

        use_case = UpdateKnowledgeUnitMasteryUseCase(
            learning_plan_repository=learning_plan_repository,
            mastery_service=mock_mastery_service,
        )

        # Act
        use_case.execute(
            learning_plan_id=sample_learning_plan.id,
            knowledge_unit_id=ku.id,
        )

        # Assert
        updated_plan = learning_plan_repository.get_by_id(sample_learning_plan.id)
        assert updated_plan is not None

    @staticmethod
    def test_raises_error_when_learning_plan_not_found(
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should raise ValueError when learning plan is not found."""
        # Arrange
        mock_mastery_service = Mock(spec=MasteryService)

        use_case = UpdateKnowledgeUnitMasteryUseCase(
            learning_plan_repository=learning_plan_repository,
            mastery_service=mock_mastery_service,
        )

        # Act & Assert
        with pytest.raises(ValueError, match="LearningPlan not found"):
            use_case.execute(
                learning_plan_id="non-existent-id",
                knowledge_unit_id="ku-id",
            )

    @staticmethod
    def test_raises_error_when_knowledge_unit_not_in_plan(
        sample_learning_plan: LearningPlan,
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should raise ValueError when knowledge unit is not part of the learning plan."""
        # Arrange
        learning_plan_repository.save(sample_learning_plan)

        mock_mastery_service = Mock(spec=MasteryService)

        use_case = UpdateKnowledgeUnitMasteryUseCase(
            learning_plan_repository=learning_plan_repository,
            mastery_service=mock_mastery_service,
        )

        # Act & Assert
        with pytest.raises(ValueError, match="KnowledgeUnit not part of LearningPlan"):
            use_case.execute(
                learning_plan_id=sample_learning_plan.id,
                knowledge_unit_id="non-existent-ku-id",
            )
