"""Tests for StartStudySessionUseCase."""
import pytest
from unittest.mock import Mock
import uuid

from application.common.exceptions import (
    LearningPlanNotFoundException,
)
from application.use_cases.start_study_session import StartStudySessionUseCase
from domain.entities.learning import LearningPlan, StudySession
from domain.entities.knowledge_unit import KnowledgeUnit
from domain.entities.question import Question, QuestionID, Difficulty, Answer
from domain.ports.question_generation import QuestionGenerationService
from domain.ports.study_focus_policy import StudyFocusPolicy
from infrastructure.adapters.learning_plan_repository import InMemoryLearningPlanRepository
from infrastructure.adapters.question_repository import InMemoryQuestionRepository


@pytest.fixture
def learning_plan_repository() -> InMemoryLearningPlanRepository:
    """Provide an in-memory learning plan repository."""
    return InMemoryLearningPlanRepository(_plans={})


@pytest.fixture
def question_repository() -> InMemoryQuestionRepository:
    """Provide an in-memory question repository."""
    return InMemoryQuestionRepository(_questions={})


class TestStartStudySessionUseCase:
    """Test suite for StartStudySessionUseCase."""

    @staticmethod
    def test_creates_study_session_for_learning_plan(
        sample_learning_plan: LearningPlan,
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
        sample_knowledge_units: list[KnowledgeUnit],
    ) -> None:
        """Should create a new study session for a learning plan."""
        # Arrange
        learning_plan_repository.save(sample_learning_plan)

        mock_policy = Mock(spec=StudyFocusPolicy)
        mock_policy.select_knowledge_units.return_value = sample_knowledge_units[:1]

        mock_question_gen = Mock(spec=QuestionGenerationService)
        sample_questions = [
            Question(
                id=QuestionID(str(uuid.uuid4())),
                text=f"Test question {i}",
                difficulty=Difficulty(level=2),
                correct_answer=Answer("Test answer"),
                knowledge_unit_id=sample_knowledge_units[0].id,
            )
            for i in range(5)
        ]
        mock_question_gen.generate_questions_batch.return_value = sample_questions

        use_case = StartStudySessionUseCase(
            learning_plan_repository=learning_plan_repository,
            study_focus_policy=mock_policy,
            question_generator=mock_question_gen,
            question_repository=question_repository,
            max_questions=5,
        )

        # Act
        result = use_case.execute(sample_learning_plan.id)

        # Assert
        assert isinstance(result, StudySession)
        assert result.max_questions == 5
        assert len(result.questions) > 0

    @staticmethod
    def test_generates_questions_for_selected_knowledge_units(
        sample_learning_plan: LearningPlan,
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
        sample_knowledge_units: list[KnowledgeUnit],
    ) -> None:
        """Should generate questions for each selected knowledge unit."""
        # Arrange
        learning_plan_repository.save(sample_learning_plan)

        mock_policy = Mock(spec=StudyFocusPolicy)
        mock_policy.select_knowledge_units.return_value = sample_knowledge_units

        def generate_batch(ku, count):
            return [
                Question(
                    id=QuestionID(str(uuid.uuid4())),
                    text=f"Question {i} about {ku.description}",
                    difficulty=Difficulty(level=2 + i),
                    correct_answer=Answer("Answer"),
                    knowledge_unit_id=ku.id,
                )
                for i in range(count)
            ]

        mock_question_gen = Mock(spec=QuestionGenerationService)
        mock_question_gen.generate_questions_batch.side_effect = generate_batch

        use_case = StartStudySessionUseCase(
            learning_plan_repository=learning_plan_repository,
            study_focus_policy=mock_policy,
            question_generator=mock_question_gen,
            question_repository=question_repository,
            max_questions=5,
        )

        # Act
        result = use_case.execute(sample_learning_plan.id)

        # Assert
        assert len(result.questions) == 5
        # With 3 KUs and 5 questions, should be called 3 times (2,2,1 distribution or 2,1,2 etc.)
        assert mock_question_gen.generate_questions_batch.call_count == len(sample_knowledge_units)

    @staticmethod
    def test_persists_questions_to_repository(
        sample_learning_plan: LearningPlan,
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
        sample_knowledge_units: list[KnowledgeUnit],
    ) -> None:
        """Should persist generated questions to the question repository."""
        # Arrange
        learning_plan_repository.save(sample_learning_plan)

        mock_policy = Mock(spec=StudyFocusPolicy)
        mock_policy.select_knowledge_units.return_value = sample_knowledge_units[:1]

        sample_questions = [
            Question(
                id=QuestionID(str(uuid.uuid4())),
                text=f"Test question {i}",
                difficulty=Difficulty(level=2),
                correct_answer=Answer("Test answer"),
                knowledge_unit_id=sample_knowledge_units[0].id,
            )
            for i in range(5)
        ]

        mock_question_gen = Mock(spec=QuestionGenerationService)
        mock_question_gen.generate_questions_batch.return_value = sample_questions

        use_case = StartStudySessionUseCase(
            learning_plan_repository=learning_plan_repository,
            study_focus_policy=mock_policy,
            question_generator=mock_question_gen,
            question_repository=question_repository,
            max_questions=5,
        )

        # Act
        use_case.execute(sample_learning_plan.id)

        # Assert
        # Check that all questions were persisted
        for sample_question in sample_questions:
            persisted_question = question_repository.get_by_id(sample_question.id)
            assert persisted_question is not None
            assert persisted_question.id == sample_question.id

    @staticmethod
    def test_adds_session_to_learning_plan(
        sample_learning_plan: LearningPlan,
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
        sample_knowledge_units: list[KnowledgeUnit],
    ) -> None:
        """Should add the created session to the learning plan."""
        # Arrange
        initial_session_count = len(sample_learning_plan.sessions)
        learning_plan_repository.save(sample_learning_plan)

        mock_policy = Mock(spec=StudyFocusPolicy)
        mock_policy.select_knowledge_units.return_value = sample_knowledge_units[:1]

        mock_question_gen = Mock(spec=QuestionGenerationService)
        sample_questions = [
            Question(
                id=QuestionID(str(uuid.uuid4())),
                text=f"Test question {i}",
                difficulty=Difficulty(level=2),
                correct_answer=Answer("Test answer"),
                knowledge_unit_id=sample_knowledge_units[0].id,
            )
            for i in range(5)
        ]
        mock_question_gen.generate_questions_batch.return_value = sample_questions

        use_case = StartStudySessionUseCase(
            learning_plan_repository=learning_plan_repository,
            study_focus_policy=mock_policy,
            question_generator=mock_question_gen,
            question_repository=question_repository,
            max_questions=5,
        )

        # Act
        result = use_case.execute(sample_learning_plan.id)

        # Assert
        updated_plan = learning_plan_repository.get_by_id(sample_learning_plan.id)
        assert len(updated_plan.sessions) == initial_session_count + 1
        assert result in updated_plan.sessions

    @staticmethod
    def test_raises_error_when_learning_plan_not_found(
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
    ) -> None:
        """Should raise LearningPlanNotFoundException when learning plan is not found."""
        # Arrange
        mock_policy = Mock(spec=StudyFocusPolicy)
        mock_question_gen = Mock(spec=QuestionGenerationService)

        use_case = StartStudySessionUseCase(
            learning_plan_repository=learning_plan_repository,
            study_focus_policy=mock_policy,
            question_generator=mock_question_gen,
            question_repository=question_repository,
            max_questions=5,
        )

        # Act & Assert
        with pytest.raises(LearningPlanNotFoundException):  # Will fail trying to access None
            use_case.execute("non-existent-plan-id")
