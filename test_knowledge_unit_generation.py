import pytest
from typing import List

# Assuming the classes and openai_llm_call are imported:
# Document, Claim, FactKnowledge, SkillKnowledge, LLMKnowledgeUnitGenerationService, openai_llm_call
from entities import Document, Claim, FactKnowledge, SkillKnowledge, LLMKnowledgeUnitGenerationService, openai_llm_call


@pytest.mark.integration
def test_llm_knowledge_unit_generation_spanish_accents():
    # --- 1. Setup: sample document ---
    doc = Document(
        id="doc_test_2",
        text=(
            "In Spanish, words stressed on the final syllable ending in 'n', 's', or a vowel carry a written accent. "
            "Words stressed on the penultimate syllable generally do not need an accent. "
            "Exceptions exist for words that break the standard stress rules."
        )
    )

    # --- 2. Initialize the service ---
    service = LLMKnowledgeUnitGenerationService(llm_call=openai_llm_call)

    # --- 3. Call the service ---
    knowledge_units: List = service.generate_knowledge_units(doc)

    # --- 4. Basic assertions ---
    assert len(knowledge_units) > 0, "No knowledge units were generated."

    fact_knowledge_found = any(isinstance(ku, FactKnowledge) for ku in knowledge_units)
    skill_knowledge_found = any(isinstance(ku, SkillKnowledge) for ku in knowledge_units)

    assert fact_knowledge_found, "No FactKnowledge was generated."
    assert skill_knowledge_found, "No SkillKnowledge was generated."

    # Ensure FactKnowledge references Claims
    for ku in knowledge_units:
        if isinstance(ku, FactKnowledge):
            assert isinstance(ku.target_claim, Claim), "FactKnowledge target_claim is not a Claim."

    # Ensure SkillKnowledge references lists of Claims
    for ku in knowledge_units:
        if isinstance(ku, SkillKnowledge):
            assert isinstance(ku.source_claims, list), "SkillKnowledge source_claims is not a list."
            assert all(isinstance(c, Claim) for c in ku.source_claims), "SkillKnowledge source_claims contain non-Claim items."
