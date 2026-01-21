from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.use_cases.get_learning_plan import GetLearningPlanUseCase
from domain.entities.learning import LearningPlan


class GetLearningPlanAPIBase(ABC):
    """Abstract base class for getting learning plan endpoints."""

    @abstractmethod
    async def get_learning_plan(self, learning_plan_id: str) -> dict:
        """Get a learning plan by ID."""
        pass


@dataclass
class GetLearningPlanAPIImpl(GetLearningPlanAPIBase):
    """Implementation of the GetLearningPlanAPIBase."""
    get_learning_plan_use_case: GetLearningPlanUseCase

    async def get_learning_plan(self, learning_plan_id: str) -> dict:
        """Get learning plan endpoint implementation."""
        plan: LearningPlan = self.get_learning_plan_use_case.execute(
            learning_plan_id=learning_plan_id
        )
        
        # FIXME: Better to do this with a DTO
        # Calculate average mastery across all knowledge units
        if plan.knowledge_units:
            avg_mastery = sum(ku.mastery_level for ku in plan.knowledge_units) / len(plan.knowledge_units)
        else:
            avg_mastery = 0.0
        
        return {
            "learning_plan_id": str(plan.id),
            "knowledge_unit_count": len(plan.knowledge_units),
            "average_mastery": round(avg_mastery, 3),
            "created_at": plan.created_at.isoformat(),
            "completed_at": plan.completed_at.isoformat() if plan.completed_at else None,
        }
