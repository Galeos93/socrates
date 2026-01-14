import pytest

from entities import (
    Claim,
    FactKnowledge,
    LLMQuestionGenerationService,
    SkillKnowledge,
    openai_llm_call,
)

@pytest.mark.integration
def test_llm_question_generation_service():
    # --- 1. Setup sample claims and knowledge units ---
    claim1 = Claim(text="Words stressed on the final syllable ending in n, s, or vowel carry a written accent.", doc_id="doc1", doc_location="")
    claim2 = Claim(text="Exceptions exist for words that break standard stress rules.", doc_id="doc1", doc_location="")

    # FactKnowledge
    fact_knowledge = FactKnowledge(
        id="fact1",
        description="Test understanding of Spanish accent rules.",
        target_claim=claim1
    )

    # SkillKnowledge
    skill_knowledge = SkillKnowledge(
        id="skill1",
        description="Apply Spanish accent rules to correctly add tildes.",
        source_claims=[claim1, claim2]
    )

    # --- 2. Initialize the service ---
    service = LLMQuestionGenerationService(llm_call=openai_llm_call)

    # --- 3. Generate questions ---
    fact_question = service.generate_next_question(fact_knowledge)
    skill_question = service.generate_next_question(skill_knowledge)

    # --- 4. Assertions ---
    # Ensure we have valid Question objects
    assert fact_question.text, "FactKnowledge question text is empty."
    assert fact_question.answer, "FactKnowledge question answer is empty."
    assert isinstance(fact_question.difficulty.level, int), "FactKnowledge difficulty level is not an int."

    assert skill_question.text, "SkillKnowledge question text is empty."
    assert skill_question.answer, "SkillKnowledge question answer is empty."
    assert isinstance(skill_question.difficulty.level, int), "SkillKnowledge difficulty level is not an int."

    # Ensure knowledge_unit references are correct
    assert fact_question.knowledge_unit == fact_knowledge
    assert skill_question.knowledge_unit == skill_knowledge

    print("Fact Question:", fact_question.text, "| Answer:", fact_question.answer)
    print("Skill Question:", skill_question.text, "| Answer:", skill_question.answer)
