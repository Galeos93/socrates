from abc import ABC, abstractmethod

from domain.entities.learning import KnowledgeUnit


class StudyFocusPolicy(ABC):
    """
    Policy interface for determining which knowledge units to focus on during a study session.
    """

    @abstractmethod
    def select_knowledge_units(self, knowledge_units: list[KnowledgeUnit], max_units: int) -> list[KnowledgeUnit]:
        """
        Selects a subset of knowledge units to focus on.

        Parameters
        ----------
        knowledge_units : list
            List of knowledge units to choose from.
        max_units : int
            Maximum number of knowledge units to select.

        Returns
        -------
        list
            Selected subset of knowledge units.
        """
        pass