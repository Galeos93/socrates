from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.use_cases.start_study_session import StartStudySessionUseCase
from domain.entities.learning import StudySession


class StartStudySessionAPIBase(ABC):
    """Abstract base class for starting study session endpoints."""

    @abstractmethod
    async def start_study_session(self, learning_plan_id: str) -> dict:
        """Start a new study session for a learning plan."""
        pass


@dataclass
class StartStudySessionAPIImpl(StartStudySessionAPIBase):
    """Implementation of the StartStudySessionAPIBase."""
    start_study_session_use_case: StartStudySessionUseCase

    async def start_study_session(self, learning_plan_id: str) -> dict:
        """Start study session endpoint implementation."""
        session: StudySession = self.start_study_session_use_case.execute(learning_plan_id)
        
        return {
            "session_id": session.id,
            "max_questions": session.max_questions,
            "question_count": len(session.questions),
            "started_at": session.started_at.isoformat(),
        }
