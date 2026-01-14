from dataclasses import dataclass
from typing import Callable, List, Dict
import json
import uuid

from domain.entities.document import Document
from domain.entities.claim import Claim
from domain.entities.knowledge_unit import KnowledgeUnit, FactKnowledge, SkillKnowledge
from infrastructure.adapters.knowledge_unit_generation.llm.prompts import (
    build_knowledge_unit_extraction_prompt
)
from infrastructure.adapters.knowledge_unit_generation.llm.openai_client import openai_llm_call


@dataclass
class LLMKnowledgeUnitGenerationService:
    llm_call: Callable[[str], str] = openai_llm_call

    def generate_knowledge_units(self, doc: Document) -> List[KnowledgeUnit]:
        """
        Generates KnowledgeUnits from a Document.

        Depending on implementation, claims may be anchored to:
        - Whole document
        - Paragraphs
        - Character ranges
        """
        prompt = build_knowledge_unit_extraction_prompt(doc.text)
        raw_response = self.llm_call(prompt)
        data = json.loads(raw_response)

        # --- Phase A: create claims ---
        claim_registry: Dict[int, Claim] = {}
        for item in data.get("claims", []):
            claim_registry[item["id"]] = Claim(
                text=item["text"],
                doc_id=doc.id,
            )

        # --- Phase B & C: Facts and Skills ---
        results: List[KnowledgeUnit] = []

        for item in data.get("facts", []):
            target_claim = claim_registry[item["target_claim_id"]]
            fact = FactKnowledge(
                id=str(uuid.uuid4()),
                description=item["description"],
                target_claim=target_claim
            )
            results.append(fact)

        for item in data.get("skills", []):
            source_claims = [claim_registry[i] for i in item["source_claim_ids"]]
            skill = SkillKnowledge(
                id=str(uuid.uuid4()),
                description=item["description"],
                source_claims=source_claims
            )
            results.append(skill)

        return results
