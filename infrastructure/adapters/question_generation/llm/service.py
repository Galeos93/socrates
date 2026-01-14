from typing import Callable

from domain.entities.knowledge_unit import KnowledgeUnit, FactKnowledge, SkillKnowledge
from domain.entities.question import Question, Difficulty, Answer
from domain.ports.question_generation import QuestionGenerationService
from infrastructure.adapters.question_generation.llm.prompts import build_question_creation_prompt


class LLMQuestionGenerationService(QuestionGenerationService):
    """A question generation service that uses an LLM to generate questions."""

    def __init__(self, llm_call: Callable[[str], str]):
        """
        Parameters
        ----------
        llm_call : Callable[[str], str]
            A function that takes a prompt string and returns the LLM's raw text output.
        """
        self.llm_call = llm_call

    def generate_next_question(self, ku: KnowledgeUnit) -> Question:
        """
        Generate a question for a KnowledgeUnit using an LLM.

        Parameters
        ----------
        ku : KnowledgeUnit
            The fact or skill to generate a question for.

        Returns
        -------
        Question
        """
        # --- 1. Build prompt based on KnowledgeUnit type ---
        prompt = build_question_creation_prompt(ku)

        # --- 2. Call the LLM ---
        raw_output = self.llm_call(prompt)

        # --- 3. Parse JSON output ---
        import json
        try:
            data = json.loads(raw_output)
            question_text = data["question_text"]
            answer_text = data["answer"]
            difficulty_level = data.get("difficulty_level", 2)  # default 2 if missing
        except (json.JSONDecodeError, KeyError):
            # fallback if LLM output fails
            question_text = ku.description
            answer_text = ku.target_claim.text if isinstance(ku, FactKnowledge) else "Answer TBD"
            difficulty_level = 2

        # --- 4. Construct Question ---
        question = Question(
            text=question_text,
            answer=Answer(answer_text),
            difficulty=Difficulty(level=difficulty_level),
            knowledge_unit=ku
        )

        return question