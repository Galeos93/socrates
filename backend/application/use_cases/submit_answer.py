from dataclasses import dataclass
import logging

from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.entities.question import Answer, QuestionID
from domain.entities.learning import StudySessionID
from application.common.exceptions import (
    LearningPlanNotFoundException,
    StudySessionNotFoundException,
    QuestionNotInStudySessionException,
)


@dataclass
class SubmitAnswerUseCase:
    """
    Records a learner's answer to a question within a StudySession.
    Does NOT assess correctness or update mastery.
    """

    learning_plan_repository: LearningPlanRepository

    def execute(
        self,
        learning_plan_id: str,
        study_session_id: StudySessionID,
        question_id: QuestionID,
        user_answer: Answer,
    ) -> None:
        logging.info("[SubmitAnswerUseCase] Submitting answer to question.")
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

        # 3. Validate question belongs to session
        session_question = session.questions.get(question_id)
        if not session_question:
            raise QuestionNotInStudySessionException(
                question_id=question_id,
                study_session_id=study_session_id
            )

        # 4. Submit answer (creates AnswerAttempt)
        session_question.submit_answer(user_answer)

        # 5. Persist aggregate
        self.learning_plan_repository.save(learning_plan)