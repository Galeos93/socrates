from dataclasses import dataclass
import logging

from application.dto.study_session_view import StudySessionView
from application.services.study_session_view import StudySessionViewService
from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository
from domain.entities.learning import LearningPlanID, StudySessionID
from domain.ports.question_repository import QuestionRepository

@dataclass
class GetStudySessionViewUseCase:
    learning_plan_repo: LearningPlanRepository
    view_service: StudySessionViewService

    def execute(
        self,
        learning_plan_id: str,
        study_session_id: str,
    ) -> StudySessionView:
        logging.info("[GetStudySessionViewUseCase] Retrieving study session view.")
        plan = self.learning_plan_repo.get_by_id(learning_plan_id)
        if not plan:
            raise ValueError("LearningPlan not found")

        sessions = [s for s in plan.sessions if s.id == study_session_id]
        if len(sessions) == 0:
            raise ValueError("StudySession not found")
        session = sessions[0]

        return self.view_service.build_view(session)