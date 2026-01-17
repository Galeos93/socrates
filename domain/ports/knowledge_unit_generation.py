from abc import ABC, abstractmethod
from typing import List


from domain.entities.document import Document
from domain.entities.knowledge_unit import KnowledgeUnit


class KnowledgeUnitGenerationService(ABC):
    @abstractmethod
    def generate_knowledge_units(
        self,
        documents: List[Document],
    ) -> list[KnowledgeUnit]:
        """Generate a KnowledgeUnit from text.

        Parameters
        ----------
        documents : List[Document]
            The documents to generate knowledge units from.

        Returns
        -------
        list[KnowledgeUnit]

        """
        pass
