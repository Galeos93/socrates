from dataclasses import dataclass

from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository
from domain.services.mastery import MasteryService
from domain.entities.knowledge_unit import KnowledgeUnit


@dataclass
class UpdateKnowledgeUnitMasteryUseCase:
    """
    Updates mastery levels for a KnowledgeUnit based on question history.
    """

    learning_plan_repository: LearningPlanRepository
    question_repository: QuestionRepository
    mastery_service: MasteryService

    def execute(
        self,
        learning_plan_id: str,
        knowledge_unit_id: str,
    ) -> KnowledgeUnit:
        # 1. Load aggregate
        learning_plan = self.learning_plan_repository.get_by_id(learning_plan_id)

        # 2. Find knowledge unit
        ku = next(
            ku for ku in learning_plan.knowledge_units
            if ku.id == knowledge_unit_id
        )

        # 3. Load all related questions
        # FIXME: This could be optimized with a query method in the repo
        questions = [
            q for q in
            self.question_repository.list_all()
            if q.knowledge_unit_id == ku.id
        ]

        # 4. Calculate mastery
        new_mastery = self.mastery_service.update_mastery(
            ku=ku,
            questions=questions,
        )

        ku.mastery_level = new_mastery

        # 5. Persist aggregate
        self.learning_plan_repository.save(learning_plan)

        return ku
