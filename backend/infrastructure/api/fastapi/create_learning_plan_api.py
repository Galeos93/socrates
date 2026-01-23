from abc import ABC, abstractmethod
from dataclasses import dataclass

from opik import opik_context
from vyper import v

from application.dto.create_learning_plan import CreateLearningPlanRequest
from application.use_cases.create_learning_plan import CreateLearningPlanFromDocumentUseCase
from domain.ports.document_repository import DocumentRepository
from domain.entities.learning import LearningPlan


class CreateLearningPlanAPIBase(ABC):
    """Abstract base class for creating learning plan endpoints."""

    @abstractmethod
    async def create_learning_plan(self, request: CreateLearningPlanRequest) -> dict:
        """Create a learning plan from a document."""
        pass


@dataclass
class CreateLearningPlanAPIImpl(CreateLearningPlanAPIBase):
    """Implementation of the CreateLearningPlanAPIBase."""
    create_learning_plan_use_case: CreateLearningPlanFromDocumentUseCase
    document_repository: DocumentRepository

    async def create_learning_plan(self, request: CreateLearningPlanRequest) -> dict:
        """Create a learning plan endpoint implementation."""
        documents = [
            self.document_repository.get_by_id(document_id)
            for document_id in request.document_ids
        ]
        documents = [doc for doc in documents if doc is not None]
        if not documents:
            raise ValueError("No valid documents found for the provided IDs")

        learning_plan: LearningPlan = self.create_learning_plan_use_case.execute(documents)

        if v.get_bool("opik.enable_tracking"):
            opik_context.update_current_trace(
                thread_id=learning_plan.id,
                tags=["learning_plan_creation"],
                metadata={
                    "learning_plan_id": learning_plan.id,
                    "document_ids": request.document_ids,
                    "knowledge_unit_ids": [ku.id for ku in learning_plan.knowledge_units],
                },
            )

        return {
            "learning_plan_id": learning_plan.id,
            "knowledge_unit_count": len(learning_plan.knowledge_units),
            "created_at": learning_plan.created_at.isoformat(),
        }
