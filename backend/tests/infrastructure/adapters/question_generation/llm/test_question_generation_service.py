import os
import pytest

from openai import OpenAI

from domain.entities.claim import Claim
from domain.entities.knowledge_unit import FactKnowledge, SkillKnowledge
from domain.entities.question import Question
from infrastructure.adapters.question_generation.llm.openai_client import openai_llm_call
from infrastructure.adapters.question_generation.llm.service import LLMQuestionGenerationService


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("OPENAI_API_KEY") is None,
    reason="Requires OPENAI_API_KEY environment variable"
)
def test_llm_question_generation_service():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    service = LLMQuestionGenerationService(client=client, model="gpt-4o")

    # --- 3. Generate questions ---
    fact_question: Question = service.generate_next_question(fact_knowledge)
    skill_question: Question = service.generate_next_question(skill_knowledge)

    # --- 4. Assertions ---
    # Ensure we have valid Question objects
    assert fact_question.text, "FactKnowledge question text is empty."
    assert fact_question.correct_answer, "FactKnowledge question answer is empty."
    assert fact_question.correct_answer != "Answer TBD"
    assert isinstance(fact_question.difficulty.level, int), "FactKnowledge difficulty level is not an int."

    assert skill_question.text, "SkillKnowledge question text is empty."
    assert skill_question.correct_answer, "SkillKnowledge question answer is empty."
    assert fact_question.correct_answer != "Answer TBD"
    assert isinstance(skill_question.difficulty.level, int), "SkillKnowledge difficulty level is not an int."

    # Ensure knowledge_unit references are correct
    assert fact_question.knowledge_unit_id == fact_knowledge.id
    assert skill_question.knowledge_unit_id == skill_knowledge.id
