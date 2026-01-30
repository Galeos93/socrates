from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from application.use_cases.list_learning_plans import ListLearningPlansUseCase
from domain.entities.learning import LearningPlan
from domain.entities.question import QuestionStatus


class ListLearningPlansAPIBase(ABC):
    """Abstract base class for listing learning plans endpoint."""

    @abstractmethod
    async def list_learning_plans(self) -> List[dict]:
        """List all active learning plans."""
        pass


@dataclass
class ListLearningPlansAPIImpl(ListLearningPlansAPIBase):
    """Implementation of the ListLearningPlansAPIBase."""
    list_learning_plans_use_case: ListLearningPlansUseCase

    async def list_learning_plans(self) -> List[dict]:
        """List all active learning plans endpoint implementation."""
        plans: List[LearningPlan] = self.list_learning_plans_use_case.execute()

        result = []
        for plan in plans:
            # Calculate average mastery across all knowledge units
            if plan.knowledge_units:
                avg_mastery = sum(ku.mastery_level for ku in plan.knowledge_units) / len(plan.knowledge_units)
            else:
                avg_mastery = 0.0

            # Find incomplete sessions (sessions without ended_at)
            incomplete_sessions = [
                {
                    "session_id": s.id,
                    "questions_answered": sum(1 for q in s.questions.values() if q.status != QuestionStatus.PENDING),
                    "total_questions": len(s.questions),
                    "max_questions": s.max_questions,
                    "started_at": s.started_at.isoformat(),
                }
                for s in plan.sessions
                if not s.is_completed()
            ]

            result.append({
                "learning_plan_id": str(plan.id),
                "knowledge_unit_count": len(plan.knowledge_units),
                "average_mastery": round(avg_mastery, 3),
                "created_at": plan.created_at.isoformat(),
                "completed_at": plan.completed_at.isoformat() if plan.completed_at else None,
                "session_count": len(plan.sessions),
                "incomplete_sessions": incomplete_sessions,
            })

        return result
