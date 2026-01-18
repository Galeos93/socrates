from dataclasses import dataclass

from domain.entities.knowledge_unit import KnowledgeUnit
from domain.ports.learning_scope_policy import LearningScopePolicy


class NaiveLearningScopePolicy(LearningScopePolicy):
    """Policy interface for determining the scope of learning for a learning plan.

    Notes
    -----
    Simply order knowledge units by importance, up to max_units.

    """

    def select_knowledge_units(
            self, knowledge_units: list[KnowledgeUnit],
            max_units: int
    ) -> list[KnowledgeUnit]:
        """
        Selects a subset of knowledge units to include in a learning plan.

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
        return sorted(knowledge_units, key=lambda ku: ku.importance, reverse=True)[:max_units]
