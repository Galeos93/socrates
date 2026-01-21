from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.use_cases.update_ku_mastery import UpdateKnowledgeUnitMasteryUseCase
from domain.entities.knowledge_unit import KnowledgeUnit


class UpdateMasteryAPIBase(ABC):
    """Abstract base class for updating knowledge unit mastery endpoints."""

    @abstractmethod
    async def update_mastery(
        self,
        learning_plan_id: str,
        knowledge_unit_id: str,
    ) -> dict:
        """Update mastery level for a knowledge unit."""
        pass


@dataclass
class UpdateMasteryAPIImpl(UpdateMasteryAPIBase):
    """Implementation of the UpdateMasteryAPIBase."""
    update_mastery_use_case: UpdateKnowledgeUnitMasteryUseCase

    async def update_mastery(
        self,
        learning_plan_id: str,
        # FIXME: Maybe KU not needed? Update all?
        knowledge_unit_id: str,
    ) -> dict:
        """Update mastery endpoint implementation."""
        ku: KnowledgeUnit = self.update_mastery_use_case.execute(
            learning_plan_id=learning_plan_id,
            knowledge_unit_id=knowledge_unit_id,
        )
        
        # Extract values to plain types to avoid circular reference during serialization
        ku_id = str(ku.id)
        mastery = float(ku.mastery_level)
        
        return {
            "knowledge_unit_id": ku_id,
            "mastery_level": mastery,
        }
