from dataclasses import dataclass
from typing import Dict, Optional

from opik import Opik, Prompt
from opik.exceptions import PromptTemplateStructureMismatch

@dataclass
class OpikPromptFactory:
    opik_client: Optional[Opik] = None
    opik_template_name: str = "KnowledgeUnitGenerationPrompt"

    def __post_init__(self):
        """Initialize Opik client if not provided."""
        if self.opik_client is None:
            self.opik_client = Opik()

    def build(self, template: str, template_arguments: Dict) -> str:
        # This saves the prompt template to Opik if not already present
        opik_prompt = Prompt(
            name=self.opik_template_name,
            prompt=template,
            metadata={"environment": "laboratory"}
        )

        return opik_prompt.format(**template_arguments)