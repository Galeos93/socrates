from dataclasses import dataclass

from application.dto.study_session_view import StudySessionView
from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository
from domain.entities.learning import LearningPlanID, StudySessionID
from domain.ports.question_repository import QuestionRepository

@dataclass
class GetStudySessionUseCase:
    plan_repo: LearningPlanRepository
    question_repo: QuestionRepository

    def execute(self, learning_plan_id: LearningPlanID, session_id: StudySessionID) -> StudySessionView:
        plan = self.plan_repo.get_by_id(learning_plan_id)
        # FIXME: Handle this inside the repository?
        session = [
            s for s in plan.sessions if s.id == session_id
        ]
        questions = [
            self.question_repo.get_by_id(q_id)
            for q_id in session.questions
        ]

        return StudySessionView.from_domain(session, questions)