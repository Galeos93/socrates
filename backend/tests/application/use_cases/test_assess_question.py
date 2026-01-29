"""Tests for AssessQuestionOutcomeUseCase."""
import pytest
import uuid
from unittest.mock import Mock

from application.common.exceptions import (
    LearningPlanNotFoundException,
    StudySessionNotFoundException,
    QuestionNotFoundException,
    QuestionNotInStudySessionException,
    NoUnassessedAnswerAttemptException,
)
from application.use_cases.assess_question import AssessQuestionOutcomeUseCase
from domain.entities.learning import LearningPlan, StudySession
from domain.entities.question import (
    Question, QuestionID, SessionQuestion, Answer, AnswerAttempt, AnswerAssessment
)
from domain.ports.answer_evaluation import AnswerEvaluationService
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


class TestAssessQuestionOutcomeUseCase:
    """Test suite for AssessQuestionOutcomeUseCase."""

    @staticmethod
    def test_evaluates_answer_correctness(
        sample_learning_plan: LearningPlan,
        sample_study_session: StudySession,
        sample_question: Question,
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
    ) -> None:
        """Should evaluate whether the user's answer is correct."""
        # Arrange
        question_id = sample_question.id
        sample_study_session.questions[question_id] = SessionQuestion(
            question_id=question_id, attempts=[
                AnswerAttempt(user_answer=Answer("Some answer"),
                              assessment=None
                )
            ]
        )
        learning_plan_repository.save(sample_learning_plan)
        question_repository.save(sample_question)

        mock_evaluator = Mock(spec=AnswerEvaluationService)
        mock_evaluator.evaluate.return_value = AnswerAssessment(
            is_correct=True,
            correct_answer=sample_question.correct_answer,
            explanation="Explanation",
            assessed_at=None,
        )

        use_case = AssessQuestionOutcomeUseCase(
            learning_plan_repository=learning_plan_repository,
            question_repository=question_repository,
            answer_evaluation_service=mock_evaluator,
        )

        user_answer = Answer("Some answer")

        # Act
        result = use_case.execute(
            learning_plan_id=sample_learning_plan.id,
            study_session_id=sample_study_session.id,
            question_id=question_id,
        )

        # Assert
        assert result == AnswerAssessment(
            is_correct=True,
            correct_answer=sample_question.correct_answer,
            explanation="Explanation",
            assessed_at=None,
        )
        mock_evaluator.evaluate.assert_called_once_with(
            question=sample_question, user_answer=user_answer
        )

    @staticmethod
    def test_marks_correctness_on_session_question(
        sample_learning_plan: LearningPlan,
        sample_study_session: StudySession,
        sample_question: Question,
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
    ) -> None:
        """Should mark the correctness on the session question."""
        # Arrange
        question_id = sample_question.id
        sample_study_session.questions[question_id] = SessionQuestion(
            question_id=question_id, attempts=[
                AnswerAttempt(user_answer=Answer("Attempt 1"),
                              assessment=None
                )
            ]
        )
        learning_plan_repository.save(sample_learning_plan)
        question_repository.save(sample_question)

        mock_evaluator = Mock(spec=AnswerEvaluationService)
        mock_evaluator.evaluate.return_value = AnswerAssessment(
            is_correct=False,
            correct_answer=sample_question.correct_answer,
            explanation="Explanation",
        )

        use_case = AssessQuestionOutcomeUseCase(
            learning_plan_repository=learning_plan_repository,
            question_repository=question_repository,
            answer_evaluation_service=mock_evaluator,
        )

        # Act
        use_case.execute(
            learning_plan_id=sample_learning_plan.id,
            study_session_id=sample_study_session.id,
            question_id=question_id,
        )

        # Assert
        updated_plan = learning_plan_repository.get_by_id(sample_learning_plan.id)
        session = updated_plan.sessions[0]
        session_question = session.questions[question_id]
        assert session_question.attempts[0].assessment.is_correct is False

    @staticmethod
    def test_persists_aggregate_after_assessment(
        sample_learning_plan: LearningPlan,
        sample_study_session: StudySession,
        sample_question: Question,
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
    ) -> None:
        """Should persist the learning plan aggregate after assessment."""
        # Arrange
        question_id = sample_question.id
        sample_study_session.questions[question_id] = SessionQuestion(
            question_id=question_id, attempts=[
                AnswerAttempt(user_answer=Answer("Attempt 1"),
                              assessment=None
                )
            ]
        )
        learning_plan_repository.save(sample_learning_plan)
        question_repository.save(sample_question)

        mock_evaluator = Mock(spec=AnswerEvaluationService)
        mock_evaluator.evaluate.return_value = True

        use_case = AssessQuestionOutcomeUseCase(
            learning_plan_repository=learning_plan_repository,
            question_repository=question_repository,
            answer_evaluation_service=mock_evaluator,
        )

        # Act
        use_case.execute(
            learning_plan_id=sample_learning_plan.id,
            study_session_id=sample_study_session.id,
            question_id=question_id,
        )

        # Assert
        updated_plan = learning_plan_repository.get_by_id(sample_learning_plan.id)
        assert updated_plan is not None

    @staticmethod
    def test_raises_error_when_learning_plan_not_found(
        question_repository: InMemoryQuestionRepository,
        learning_plan_repository: InMemoryLearningPlanRepository,
    ) -> None:
        """Should raise LearningPlanNotFoundException when learning plan is not found."""
        # Arrange
        mock_evaluator = Mock(spec=AnswerEvaluationService)

        use_case = AssessQuestionOutcomeUseCase(
            learning_plan_repository=learning_plan_repository,
            question_repository=question_repository,
            answer_evaluation_service=mock_evaluator,
        )

        # Act & Assert
        with pytest.raises(LearningPlanNotFoundException):
            use_case.execute(
                learning_plan_id="non-existent-id",
                study_session_id="session-id",
                question_id=QuestionID("question-id"),
            )

    @staticmethod
    def test_raises_error_when_study_session_not_found(
        sample_learning_plan: LearningPlan,
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
    ) -> None:
        """Should raise StudySessionNotFoundException when study session is not found."""
        # Arrange
        learning_plan_repository.save(sample_learning_plan)

        mock_evaluator = Mock(spec=AnswerEvaluationService)

        use_case = AssessQuestionOutcomeUseCase(
            learning_plan_repository=learning_plan_repository,
            question_repository=question_repository,
            answer_evaluation_service=mock_evaluator,
        )

        # Act & Assert
        with pytest.raises(StudySessionNotFoundException):
            use_case.execute(
                learning_plan_id=sample_learning_plan.id,
                study_session_id="non-existent-session-id",
                question_id=QuestionID("question-id"),
            )

    @staticmethod
    def test_raises_error_when_question_not_in_session(
        sample_learning_plan: LearningPlan,
        sample_study_session: StudySession,
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
    ) -> None:
        """Should raise QuestionNotInStudySessionException when question is not part of the session."""
        # Arrange
        learning_plan_repository.save(sample_learning_plan)

        mock_evaluator = Mock(spec=AnswerEvaluationService)

        use_case = AssessQuestionOutcomeUseCase(
            learning_plan_repository=learning_plan_repository,
            question_repository=question_repository,
            answer_evaluation_service=mock_evaluator,
        )

        # Act & Assert
        with pytest.raises(QuestionNotInStudySessionException):
            use_case.execute(
                learning_plan_id=sample_learning_plan.id,
                study_session_id=sample_study_session.id,
                question_id=QuestionID("non-existent-question-id"),
            )

    @staticmethod
    def test_raises_error_when_question_not_found_in_repository(
        sample_learning_plan: LearningPlan,
        sample_study_session: StudySession,
        learning_plan_repository: InMemoryLearningPlanRepository,
        question_repository: InMemoryQuestionRepository,
    ) -> None:
        """Should raise QuestionNotFoundException when canonical question is not found."""
        # Arrange
        question_id = QuestionID(str(uuid.uuid4()))
        sample_study_session.questions[question_id] = SessionQuestion(
            question_id=question_id, attempts=[
                AnswerAttempt(user_answer=Answer("Attempt 1"),
                              assessment=None
                )
            ]
        )
        learning_plan_repository.save(sample_learning_plan)
        # Note: not saving question to repository

        mock_evaluator = Mock(spec=AnswerEvaluationService)

        use_case = AssessQuestionOutcomeUseCase(
            learning_plan_repository=learning_plan_repository,
            question_repository=question_repository,
            answer_evaluation_service=mock_evaluator,
        )

        # Act & Assert
        with pytest.raises(QuestionNotFoundException, match=f"Question with ID '{question_id}' not found"):
            use_case.execute(
                learning_plan_id=sample_learning_plan.id,
                study_session_id=sample_study_session.id,
                question_id=question_id,
            )
