from domain.ports.study_focus_policy import StudyFocusPolicy
from domain.entities.knowledge_unit import KnowledgeUnit


class NaiveStudyFocusPolicy(StudyFocusPolicy):
    """
    Policy interface for determining which knowledge units to focus on during a study session.

    Notes
    -----
    Simply order knowledge units as they are provided, up to max_units.
    """

    def select_knowledge_units(
        self, knowledge_units: list[KnowledgeUnit],
        max_units: int
    ) -> list[KnowledgeUnit]:
        """Selects a subset of knowledge units to focus on.

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


class WeightedStudyFocusPolicy(StudyFocusPolicy):
    """
    Policy interface for determining which knowledge units to focus on during a study session.

    Notes
    -----
    Selects knowledge units based on a weighted score of importance and mastery level.
    """

    def select_knowledge_units(
        self, knowledge_units: list[KnowledgeUnit],
        max_units: int
    ) -> list[KnowledgeUnit]:
        """Selects a subset of knowledge units to focus on.

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
        def score(ku: KnowledgeUnit) -> float:
            # Higher importance and lower mastery yield higher scores
            return ku.importance * (1.0 - ku.mastery_level)

        return sorted(knowledge_units, key=score, reverse=True)[:max_units]


class IdentityStudyFocusPolicy(StudyFocusPolicy):
    """
    Policy interface for determining which knowledge units to focus on during a study session.

    Notes
    -----
    Returns all knowledge units as they are provided, up to max_units.
    """

    def select_knowledge_units(
        self, knowledge_units: list[KnowledgeUnit],
        max_units: int
    ) -> list[KnowledgeUnit]:
        """Selects a subset of knowledge units to focus on.

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
        return knowledge_units[:max_units]