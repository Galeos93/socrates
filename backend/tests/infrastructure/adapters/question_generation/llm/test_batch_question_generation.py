import os
import pytest

from openai import OpenAI

from domain.entities.claim import Claim
from domain.entities.knowledge_unit import FactKnowledge, SkillKnowledge
from domain.entities.question import Question
from infrastructure.adapters.question_generation.llm.service import LLMQuestionGenerationService


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("OPENAI_API_KEY") is None,
    reason="Requires OPENAI_API_KEY environment variable"
)
class TestBatchQuestionGeneration:
    """Test batch question generation to ensure diverse questions are created."""

    @staticmethod
    def test_batch_question_generation_fact_knowledge():
        """Test that batch generation creates diverse questions for FactKnowledge."""
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Setup sample claim and fact knowledge
        claim = Claim(
            text="Words stressed on the final syllable ending in n, s, or vowel carry a written accent.",
            doc_id="doc1",
            doc_location=""
        )

        fact_knowledge = FactKnowledge(
            id="fact1",
            description="Understand Spanish accent rules for final syllable stress.",
            target_claim=claim,
            mastery_level=0.5  # Moderate mastery
        )

        # Initialize service
        service = LLMQuestionGenerationService(client=client, model="gpt-4o")

        # Generate batch of questions
        count = 3
        questions = service.generate_questions_batch(fact_knowledge, count)

        # Assertions
        assert len(questions) == count, f"Expected {count} questions, got {len(questions)}"
        
        # All questions should be valid
        for question in questions:
            assert question.text, "Question text is empty"
            assert question.correct_answer, "Question answer is empty"
            assert isinstance(question.difficulty.level, int), "Difficulty level is not an int"
            assert question.knowledge_unit_id == fact_knowledge.id, "Wrong knowledge unit reference"

        # Questions should be different
        question_texts = [q.text for q in questions]
        assert len(set(question_texts)) == count, "Questions are not diverse - duplicates found"

    @staticmethod
    def test_batch_question_generation_skill_knowledge():
        """Test that batch generation creates diverse questions for SkillKnowledge."""
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Setup sample claims and skill knowledge
        claim1 = Claim(
            text="Words stressed on the final syllable ending in n, s, or vowel carry a written accent.",
            doc_id="doc1",
            doc_location=""
        )
        claim2 = Claim(
            text="Words ending in consonants other than n or s are stressed on the final syllable without accent.",
            doc_id="doc1",
            doc_location=""
        )

        skill_knowledge = SkillKnowledge(
            id="skill1",
            description="Apply Spanish accent rules to correctly add tildes to words.",
            source_claims=[claim1, claim2],
            mastery_level=0.2  # Low mastery
        )

        # Initialize service
        service = LLMQuestionGenerationService(client=client, model="gpt-4o")

        # Generate batch of questions
        count = 4
        questions = service.generate_questions_batch(skill_knowledge, count)

        # Assertions
        assert len(questions) == count, f"Expected {count} questions, got {len(questions)}"
        
        # All questions should be valid
        for question in questions:
            assert question.text, "Question text is empty"
            assert question.correct_answer, "Question answer is empty"
            assert isinstance(question.difficulty.level, int), "Difficulty level is not an int"
            assert question.knowledge_unit_id == skill_knowledge.id, "Wrong knowledge unit reference"

        # Questions should be different
        question_texts = [q.text for q in questions]
        assert len(set(question_texts)) == count, "Questions are not diverse - duplicates found"

    @staticmethod
    def test_batch_adapts_to_mastery_level():
        """Test that batch generation adapts difficulty to mastery level."""
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        claim = Claim(
            text="Python uses indentation to define code blocks.",
            doc_id="doc1",
            doc_location=""
        )

        # High mastery knowledge unit
        high_mastery_ku = FactKnowledge(
            id="fact_high",
            description="Understanding of Python code block structure.",
            target_claim=claim,
            mastery_level=0.9  # High mastery
        )

        service = LLMQuestionGenerationService(client=client, model="gpt-4o")

        # Generate questions for high mastery
        high_mastery_questions = service.generate_questions_batch(high_mastery_ku, 2)

        # Questions for high mastery should tend toward higher difficulty
        avg_difficulty_high = sum(q.difficulty.level for q in high_mastery_questions) / len(high_mastery_questions)
        
        # At high mastery, average difficulty should be >= 3
        assert avg_difficulty_high >= 3, f"High mastery questions should be harder, got avg difficulty {avg_difficulty_high}"
