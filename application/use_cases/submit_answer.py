from dataclasses import dataclass
from datetime import datetime, UTC

from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository
from domain.entities.question import Answer, QuestionID, AnswerAttempt
from domain.entities.learning import LearningPlan, StudySession


@dataclass
class SubmitAnswerUseCase:
    """
    Records a learner's answer to a question within a StudySession.
    Does NOT assess correctness or update mastery.
    """

    learning_plan_repository: LearningPlanRepository
    question_repository: QuestionRepository

    def execute(
        self,
        learning_plan_id: str,
        study_session_id: str,
        question_id: str,
        user_answer: Answer,
    ) -> None:
        # 1. Load aggregate root
        learning_plan = self.learning_plan_repository.get_by_id(learning_plan_id)
        if not learning_plan:
            raise ValueError("LearningPlan not found")

        # 2. Locate study session (aggregate responsibility)
        session: StudySession = next(
            (s for s in learning_plan.sessions if s.id == study_session_id),
            None
        )
        if not session:
            raise ValueError("StudySession not found in LearningPlan")

        # 3. Validate question belongs to session
        if question_id not in session.questions:
            raise ValueError("Question does not belong to this StudySession")

        # 4. Load question entity
        question = self.question_repository.get_by_id(question_id)

        # 5. Update question statistics
        question.times_asked += 1

        # 6. Record answer attempt
        answer_attempt = AnswerAttempt(
            user_answer=user_answer,
            answered_at=datetime.now(UTC),
        )
        question.attempts.append(answer_attempt)


        # 7. Persist question
        self.question_repository.save(question)

        # 8. Persist aggregate root (session state may evolve later)
        self.learning_plan_repository.save(learning_plan)
