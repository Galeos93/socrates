from dataclasses import dataclass
import logging

from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository
from domain.ports.answer_evaluation import AnswerEvaluationService
from domain.entities.question import (
    QuestionID, AnswerAssessment, SessionQuestion, AnswerAttempt
)
from domain.entities.learning import StudySessionID
from application.common.exceptions import (
    LearningPlanNotFoundException,
    StudySessionNotFoundException,
    QuestionNotFoundException,
    QuestionNotInStudySessionException,
    NoUnassessedAnswerAttemptException,
)



@dataclass
class AssessQuestionOutcomeUseCase:
    """
    Determines whether a submitted answer is correct and updates
    session-specific state.
    """

    learning_plan_repository: LearningPlanRepository
    question_repository: QuestionRepository
    answer_evaluation_service: AnswerEvaluationService

    def execute(
        self,
        learning_plan_id: str,
        study_session_id: StudySessionID,
        question_id: QuestionID,
    ) -> AnswerAssessment:
        logging.info("[AssessQuestionOutcomeUseCase] Assessing question outcome.")

        # 1. Load aggregate root
        learning_plan = self.learning_plan_repository.get_by_id(learning_plan_id)
        if not learning_plan:
            raise LearningPlanNotFoundException(learning_plan_id=learning_plan_id)

        # 2. Locate study session
        session = next(
            (s for s in learning_plan.sessions if s.id == study_session_id),
            None
        )
        if not session:
            raise StudySessionNotFoundException(study_session_id=study_session_id)

        # 3. Locate session question
        session_question: SessionQuestion = session.questions.get(question_id)
        if not session_question:
            raise QuestionNotInStudySessionException(
                question_id=question_id,
                study_session_id=study_session_id
            )

        # 4. Get latest unanswered attempt
        attempt: AnswerAttempt = session_question.latest_unassessed_attempt()
        if not attempt:
            raise NoUnassessedAnswerAttemptException(question_id=question_id)

        # 5. Load canonical question
        question = self.question_repository.get_by_id(question_id)
        if not question:
            raise QuestionNotFoundException(question_id=question_id)

        # 6. Evaluate
        assessment = self.answer_evaluation_service.evaluate(
            question=question,
            user_answer=attempt.user_answer,
        )

        # 7. Attach assessment to attempt
        session_question.attach_assessment(attempt, assessment)

        # 8. Persist aggregate
        self.learning_plan_repository.save(learning_plan)

        return assessment
