"""Tests for CreateLearningPlanFromDocumentUseCase."""
import pytest
from unittest.mock import Mock
import uuid

from application.common.exceptions import (
    KUNotGeneratedException
)
from application.use_cases.create_learning_plan import (
    CreateLearningPlanFromDocumentUseCase,
)
from domain.entities.document import Document
from domain.entities.learning import LearningPlan
from domain.entities.knowledge_unit import KnowledgeUnit
from domain.ports.knowledge_unit_generation import KnowledgeUnitGenerationService
from domain.ports.learning_scope_policy import LearningScopePolicy
from infrastructure.adapters.learning_plan_repository import InMemoryLearningPlanRepository


@pytest.fixture
def learning_plan_repository() -> InMemoryLearningPlanRepository:
    """Provide an in-memory learning plan repository."""
    return InMemoryLearningPlanRepository(_plans={})


class TestCreateLearningPlanFromDocumentUseCase:
    """Test suite for CreateLearningPlanFromDocumentUseCase."""

    @staticmethod
    def test_creates_learning_plan_from_document(
        sample_document: Document,
        sample_knowledge_units: list[KnowledgeUnit],
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should create a learning plan from a document with generated knowledge units."""
        # Arrange
        mock_ku_generator = Mock(spec=KnowledgeUnitGenerationService)
        mock_ku_generator.generate_knowledge_units.return_value = sample_knowledge_units

        mock_policy = Mock(spec=LearningScopePolicy)
        mock_policy.select_knowledge_units.return_value = sample_knowledge_units

        use_case = CreateLearningPlanFromDocumentUseCase(
            ku_generator=mock_ku_generator,
            learning_scope_policy=mock_policy,
            learning_plan_repository=learning_plan_repository,
        )

        # Act
        result = use_case.execute(sample_document)

        # Assert
        assert isinstance(result, LearningPlan)
        assert len(result.knowledge_units) == len(sample_knowledge_units)
        assert result.knowledge_units == sample_knowledge_units
        assert result.sessions == []
        mock_ku_generator.generate_knowledge_units.assert_called_once_with(sample_document)
        mock_policy.select_knowledge_units.assert_called_once()

    @staticmethod
    def test_persists_learning_plan_to_repository(
        sample_document: Document,
        sample_knowledge_units: list[KnowledgeUnit],
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should persist the created learning plan to the repository."""
        # Arrange
        mock_ku_generator = Mock(spec=KnowledgeUnitGenerationService)
        mock_ku_generator.generate_knowledge_units.return_value = sample_knowledge_units

        mock_policy = Mock(spec=LearningScopePolicy)
        mock_policy.select_knowledge_units.return_value = sample_knowledge_units

        use_case = CreateLearningPlanFromDocumentUseCase(
            ku_generator=mock_ku_generator,
            learning_scope_policy=mock_policy,
            learning_plan_repository=learning_plan_repository,
        )

        # Act
        result = use_case.execute(sample_document)

        # Assert
        persisted_plan = learning_plan_repository.get_by_id(result.id)
        assert persisted_plan is not None
        assert persisted_plan.id == result.id
        assert persisted_plan.knowledge_units == result.knowledge_units

    @staticmethod
    def test_applies_learning_scope_policy(
        sample_document: Document,
        sample_knowledge_units: list[KnowledgeUnit],
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should apply the learning scope policy to filter knowledge units."""
        # Arrange
        mock_ku_generator = Mock(spec=KnowledgeUnitGenerationService)
        mock_ku_generator.generate_knowledge_units.return_value = sample_knowledge_units

        # Policy returns only first knowledge unit
        filtered_kus = [sample_knowledge_units[0]]
        mock_policy = Mock(spec=LearningScopePolicy)
        mock_policy.select_knowledge_units.return_value = filtered_kus

        use_case = CreateLearningPlanFromDocumentUseCase(
            ku_generator=mock_ku_generator,
            learning_scope_policy=mock_policy,
            learning_plan_repository=learning_plan_repository,
        )

        # Act
        result = use_case.execute(sample_document)

        # Assert
        assert len(result.knowledge_units) == 1
        assert result.knowledge_units == filtered_kus

    @staticmethod
    def test_raises_error_when_no_knowledge_units_generated(
        sample_document: Document,
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should raise KUNotGeneratedException when no knowledge units are generated."""
        # Arrange
        mock_ku_generator = Mock(spec=KnowledgeUnitGenerationService)
        mock_ku_generator.generate_knowledge_units.return_value = []

        mock_policy = Mock(spec=LearningScopePolicy)
        mock_policy.select_knowledge_units.return_value = []

        use_case = CreateLearningPlanFromDocumentUseCase(
            ku_generator=mock_ku_generator,
            learning_scope_policy=mock_policy,
            learning_plan_repository=learning_plan_repository,
        )

        # Act & Assert
        with pytest.raises(KUNotGeneratedException, match="No knowledge units could be generated from document"):
            use_case.execute(sample_document)
