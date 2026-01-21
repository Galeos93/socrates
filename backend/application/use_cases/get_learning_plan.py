from dataclasses import dataclass
import logging

from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.entities.learning import LearningPlan


@dataclass
class GetLearningPlanUseCase:
    """
    Retrieves a LearningPlan by ID.
    """

    learning_plan_repository: LearningPlanRepository

    def execute(self, learning_plan_id: str) -> LearningPlan:
        logging.info("[GetLearningPlanUseCase] Retrieving learning plan.")
        
        plan = self.learning_plan_repository.get_by_id(learning_plan_id)
        if not plan:
            raise ValueError("LearningPlan not found")
        
        return plan
