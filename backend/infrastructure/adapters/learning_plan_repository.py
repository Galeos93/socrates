from dataclasses import dataclass
from typing import Dict, Optional, List

from domain.entities.learning import LearningPlan
from domain.ports.learning_plan_repository import LearningPlanRepository


@dataclass
class InMemoryLearningPlanRepository(LearningPlanRepository):
    """In-memory implementation of LearningPlanRepository.

    Notes
    -----

    Stores LearningPlan aggregates in a dictionary keyed by plan ID.
    Intended for testing and local development.

    """
    _plans: Dict[str, LearningPlan]

    def save(self, plan: LearningPlan) -> None:
        """
        Persist the entire LearningPlan aggregate.
        """
        self._plans[plan.id] = plan

    def get_by_id(self, plan_id: str) -> Optional[LearningPlan]:
        """
        Retrieve a LearningPlan by ID.
        """
        return self._plans.get(plan_id)

    def list_active(self) -> List[LearningPlan]:
        """
        List all non-completed LearningPlans.
        """
        return [
            plan
            for plan in self._plans.values()
            if not plan.is_completed()
        ]

    def delete(self, plan_id: str) -> None:
        """
        Delete a LearningPlan and all owned state.
        """
        self._plans.pop(plan_id, None)
