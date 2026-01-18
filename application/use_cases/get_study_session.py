from dataclasses import dataclass

from application.dto.study_session_view import StudySessionView
from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository
from domain.entities.learning import LearningPlanID, StudySessionID
from domain.ports.question_repository import QuestionRepository

@dataclass
class GetStudySessionViewUseCase:
    learning_plan_repo: LearningPlanRepository
    view_service: 'StudySessionViewService'

    def execute(
        self,
        learning_plan_id: str,
        study_session_id: str,
    ) -> StudySessionView:
        plan = self.learning_plan_repo.get_by_id(learning_plan_id)
        if not plan:
            raise ValueError("LearningPlan not found")

        session = plan.get_session(study_session_id)
        if not session:
            raise ValueError("StudySession not found")

        return self.view_service.build_view(session)