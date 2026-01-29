from dataclasses import dataclass
import logging

from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository
from domain.services.mastery import MasteryService
from domain.entities.learning import SessionQuestion
from domain.entities.knowledge_unit import KnowledgeUnit
from domain.entities.question import QuestionStatus
from application.common.exceptions import (
    LearningPlanNotFoundException,
    KUNotInLearningPlanException,
)


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
        logging.info("[UpdateKnowledgeUnitMasteryUseCase] Updating knowledge unit mastery.")
        # 1. Load aggregate root
        plan = self.learning_plan_repository.get_by_id(learning_plan_id)
        if not plan:
            raise LearningPlanNotFoundException(learning_plan_id=learning_plan_id)

        # 2. Find KnowledgeUnit
        ku = next(
            (ku for ku in plan.knowledge_units if ku.id == knowledge_unit_id),
            None
        )
        if not ku:
            raise KUNotInLearningPlanException(
                knowledge_unit_id=knowledge_unit_id,
                learning_plan_id=learning_plan_id
            )

        # 3. Collect session questions for this KU
        session_questions: list[SessionQuestion] = []

        for session in plan.sessions:
            for sq in session.questions.values():
                if sq.knowledge_unit_id == ku.id and sq.status != QuestionStatus.PENDING:
                    session_questions.append(sq)

        # 4. Update mastery
        self.mastery_service.update_mastery(
            ku=ku,
            session_questions=session_questions,
        )

        # 5. Persist aggregate
        self.learning_plan_repository.save(plan)

        return ku
