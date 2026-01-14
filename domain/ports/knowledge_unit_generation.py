from abc import ABC, abstractmethod


from domain.entities.knowledge_unit import KnowledgeUnit


class KnowledgeUnitGenerationService(ABC):
    @abstractmethod
    def generate_knowledge_unit(
        self,
        text: str,
    ) -> list[KnowledgeUnit]:
        """Generate a KnowledgeUnit from text.

        Parameters
        ----------
        text: str
            The text to generate the KnowledgeUnits from.

        Returns
        -------
        list[KnowledgeUnit]

        """
        pass
