from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities.learning import LearningPlan


class LearningPlanRepository(ABC):
    """
    Repository for the LearningPlan aggregate root.

    The LearningPlan is the aggregate root and owns:
    - StudySessions
    - The association to KnowledgeUnits

    No other repository should persist or load StudySessions independently.
    """

    @abstractmethod
    def save(self, plan: LearningPlan) -> None:
        """
        Persist a LearningPlan.

        This must persist the entire aggregate:
        - LearningPlan
        - StudySessions
        - Session state
        """
        pass

    @abstractmethod
    def get_by_id(self, plan_id: str) -> Optional[LearningPlan]:
        """
        Retrieve a LearningPlan by its ID.
        """
        pass

    @abstractmethod
    def list_active(self) -> List[LearningPlan]:
        """
        List all active (non-completed) learning plans.
        """
        pass

    @abstractmethod
    def delete(self, plan_id: str) -> None:
        """
        Delete a LearningPlan and its owned sessions.
        """
        pass