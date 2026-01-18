from dataclasses import dataclass
from datetime import datetime, UTC

from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository
from domain.entities.question import Answer, QuestionID, AnswerAttempt
from domain.entities.learning import LearningPlan, StudySession, LearningPlanID, StudySessionID


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
        study_session_id: str,
        question_id: str,
    ) -> None:
        # 1. Load aggregate root
        learning_plan = self.learning_plan_repository.get_by_id(learning_plan_id)
        if not learning_plan:
            raise ValueError("LearningPlan not found")

        # 2. Locate study session
        session: StudySession = next(
            (s for s in learning_plan.sessions if s.id == study_session_id),
            None
        )
        if not session:
            raise ValueError("StudySession not found")

        # 3. Validate question belongs to session
        if question_id not in session.questions:
            raise ValueError("Question not part of this StudySession")

        # 4. Register attempt (correctness decided later)
        session.questions[question_id].register_attempt()

        # 5. Persist aggregate
        self.learning_plan_repository.save(learning_plan)
