from abc import ABC, abstractmethod

from typing import Optional


class PromptTemplateRepository(ABC):
    @abstractmethod
    def get(
        self,
        name: str,
        version: Optional[str] = None,
    ) -> str:
        """Returns the prompt template content.

        Notes
        -----
        The variables in the template MUST be indicated with double curly braces,
        e.g. {{ variable_name }}.

        Parameters
        ----------
        name : str
            Name of the prompt template.
        version : str
            Version of the prompt template.

        Returns
        -------
        str
            Prompt template content.

        """
        pass


    @abstractmethod
    def save(
        self,
        name: str,
        content: str,
        version: Optional[str] = None,
    ) -> None:
        """Saves a prompt template.

        Parameters
        ----------
        name : str
            Name of the prompt template.
        content : str
            Content of the prompt template.
        version : str
            Version of the prompt template.

        """
        pass
