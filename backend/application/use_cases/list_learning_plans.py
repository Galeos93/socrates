from dataclasses import dataclass
import logging
from typing import List

from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.entities.learning import LearningPlan


@dataclass
class ListLearningPlansUseCase:
    """
    Lists all active (non-completed) learning plans.
    """

    learning_plan_repository: LearningPlanRepository

    def execute(self) -> List[LearningPlan]:
        logging.info("[ListLearningPlansUseCase] Listing active learning plans.")
        return self.learning_plan_repository.list_active()
