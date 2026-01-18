from dataclasses import dataclass

from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository
from domain.services.mastery import MasteryService
from domain.entities.learning import SessionQuestion
from domain.entities.knowledge_unit import KnowledgeUnit


@dataclass
class UpdateKnowledgeUnitMasteryUseCase:
    """
    Updates mastery for a KnowledgeUnit based on StudySession outcomes
    within a LearningPlan.
    """

    learning_plan_repository: LearningPlanRepository
    mastery_service: MasteryService

    def execute(
        self,
        learning_plan_id: str,
        knowledge_unit_id: str,
    ) -> KnowledgeUnit:

        # 1. Load aggregate root
        plan = self.learning_plan_repository.get_by_id(learning_plan_id)
        if not plan:
            raise ValueError("LearningPlan not found")

        # 2. Find KnowledgeUnit
        ku = next(
            (ku for ku in plan.knowledge_units if ku.id == knowledge_unit_id),
            None
        )
        if not ku:
            raise ValueError("KnowledgeUnit not part of LearningPlan")

        # 3. Collect session questions for this KU
        session_questions: list[SessionQuestion] = []

        for session in plan.sessions:
            for sq in session.questions.values():
                if sq.knowledge_unit_id == ku.id and sq.is_correct is not None:
                    session_questions.append(sq)

        # 4. Calculate mastery
        new_mastery = self.mastery_service.update_mastery(
            knowledge_unit=ku,
            session_questions=session_questions,
        )

        # 5. Apply mastery
        ku.mastery_level = new_mastery

        # 6. Persist aggregate
        self.learning_plan_repository.save(plan)

        return ku
