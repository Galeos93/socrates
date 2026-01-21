from dataclasses import dataclass
import logging
from typing import List
from datetime import datetime, UTC
import uuid


from domain.entities.document import Document
from domain.entities.learning import LearningPlan
from domain.entities.knowledge_unit import KnowledgeUnit
from domain.ports.learning_scope_policy import LearningScopePolicy
from domain.ports.knowledge_unit_generation import KnowledgeUnitGenerationService
from domain.ports.learning_plan_repository import LearningPlanRepository


@dataclass
class CreateLearningPlanFromDocumentUseCase:
    """
    Application use case that creates a LearningPlan from a Document.

    This use case:
    - Generates KnowledgeUnits from a Document
    - Optionally filters / ranks them (policy hook)
    - Creates a LearningPlan aggregate
    - Persists the LearningPlan
    """

    ku_generator: KnowledgeUnitGenerationService
    learning_scope_policy: LearningScopePolicy
    learning_plan_repository: LearningPlanRepository

    def execute(self, documents: List[Document]) -> LearningPlan:
        logging.info("[CreateLearningPlanFromDocumentUseCase] Creating learning plan from documents.")
        # 1. Generate knowledge units from the document
        knowledge_units = self.ku_generator.generate_knowledge_units(documents)

        # 2. Apply learning scope policy
        knowledge_units = self.learning_scope_policy.select_knowledge_units(
            knowledge_units,
            max_units=10  # Example max_units, adjust as needed
        )

        if not knowledge_units:
            raise ValueError("No knowledge units could be generated from document")

        # 3. Create the LearningPlan aggregate
        learning_plan = LearningPlan(
            id=str(uuid.uuid4()),
            knowledge_units=knowledge_units,
            sessions=[],
            created_at=datetime.now(UTC),
        )

        # 4. Persist the LearningPlan (aggregate root)
        self.learning_plan_repository.save(learning_plan)

        return learning_plan