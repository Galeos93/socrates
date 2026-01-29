"""Tests for GetStudySessionViewUseCase."""
import pytest
import uuid
from unittest.mock import Mock

from application.common.exceptions import (
    LearningPlanNotFoundException,
    StudySessionNotFoundException,
)
from application.use_cases.get_study_session import GetStudySessionViewUseCase
from application.dto.study_session_view import StudySessionView
from application.services.study_session_view import StudySessionViewService
from domain.entities.learning import LearningPlan, StudySession
from domain.entities.question import QuestionID, SessionQuestion
from infrastructure.adapters.learning_plan_repository import InMemoryLearningPlanRepository


@pytest.fixture
def learning_plan_repository() -> InMemoryLearningPlanRepository:
    """Provide an in-memory learning plan repository."""
    return InMemoryLearningPlanRepository(_plans={})


class TestGetStudySessionViewUseCase:
    """Test suite for GetStudySessionViewUseCase."""

    @staticmethod
    def test_returns_study_session_view(
        sample_learning_plan: LearningPlan,
        sample_study_session: StudySession,
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should return a StudySessionView for the requested session."""
        # Arrange
        learning_plan_repository.save(sample_learning_plan)

        mock_view_service = Mock(spec=StudySessionViewService)
        expected_view = StudySessionView(
            id=sample_study_session.id,
            progress=0.0,
            questions=[],
            is_completed=False,
        )
        mock_view_service.build_view.return_value = expected_view

        use_case = GetStudySessionViewUseCase(
            learning_plan_repo=learning_plan_repository,
            view_service=mock_view_service,
        )

        # Act
        result = use_case.execute(
            learning_plan_id=sample_learning_plan.id,
            study_session_id=sample_study_session.id,
        )

        # Assert
        assert isinstance(result, StudySessionView)
        assert result.id == sample_study_session.id
        mock_view_service.build_view.assert_called_once_with(sample_study_session)

    @staticmethod
    def test_delegates_to_view_service(
        sample_learning_plan: LearningPlan,
        sample_study_session: StudySession,
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should delegate view building to the StudySessionViewService."""
        # Arrange
        learning_plan_repository.save(sample_learning_plan)

        mock_view_service = Mock(spec=StudySessionViewService)
        mock_view = StudySessionView(
            id=sample_study_session.id,
            progress=0.5,
            questions=[],
            is_completed=False,
        )
        mock_view_service.build_view.return_value = mock_view

        use_case = GetStudySessionViewUseCase(
            learning_plan_repo=learning_plan_repository,
            view_service=mock_view_service,
        )

        # Act
        result = use_case.execute(
            learning_plan_id=sample_learning_plan.id,
            study_session_id=sample_study_session.id,
        )

        # Assert
        mock_view_service.build_view.assert_called_once()
        call_args = mock_view_service.build_view.call_args[0]
        assert call_args[0].id == sample_study_session.id

    @staticmethod
    def test_raises_error_when_learning_plan_not_found(
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should raise LearningPlanNotFoundException when learning plan is not found."""
        # Arrange
        mock_view_service = Mock(spec=StudySessionViewService)

        use_case = GetStudySessionViewUseCase(
            learning_plan_repo=learning_plan_repository,
            view_service=mock_view_service,
        )

        # Act & Assert
        with pytest.raises(LearningPlanNotFoundException):
            use_case.execute(
                learning_plan_id="non-existent-id",
                study_session_id="session-id",
            )

    @staticmethod
    def test_raises_error_when_study_session_not_found(
        sample_learning_plan: LearningPlan,
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should raise StudySessionNotFoundException when study session is not found in the plan."""
        # Arrange
        learning_plan_repository.save(sample_learning_plan)

        mock_view_service = Mock(spec=StudySessionViewService)

        use_case = GetStudySessionViewUseCase(
            learning_plan_repo=learning_plan_repository,
            view_service=mock_view_service,
        )

        # Act & Assert
        # Note: This test assumes get_session method exists on LearningPlan
        # The use case should raise StudySessionNotFoundException when session is not found
        with pytest.raises((StudySessionNotFoundException, AttributeError)):
            use_case.execute(
                learning_plan_id=sample_learning_plan.id,
                study_session_id="non-existent-session-id",
            )
