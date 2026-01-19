from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.use_cases.get_study_session import GetStudySessionViewUseCase
from application.dto.study_session_view import StudySessionView


class GetStudySessionAPIBase(ABC):
    """Abstract base class for getting study session endpoints."""

    @abstractmethod
    async def get_study_session(self, learning_plan_id: str, session_id: str) -> StudySessionView:
        """Get a study session view."""
        pass


@dataclass
class GetStudySessionAPIImpl(GetStudySessionAPIBase):
    """Implementation of the GetStudySessionAPIBase."""
    get_study_session_use_case: GetStudySessionViewUseCase

    async def get_study_session(self, learning_plan_id: str, session_id: str) -> StudySessionView:
        """Get study session endpoint implementation."""
        return self.get_study_session_use_case.execute(
            learning_plan_id=learning_plan_id,
            study_session_id=session_id,
        )
