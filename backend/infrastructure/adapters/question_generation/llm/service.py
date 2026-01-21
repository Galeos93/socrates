from dataclasses import dataclass
from typing import Callable
import uuid
import json

from domain.entities.knowledge_unit import KnowledgeUnit, FactKnowledge, SkillKnowledge
from domain.entities.question import Question, Difficulty, Answer
from domain.ports.question_generation import QuestionGenerationService
from infrastructure.adapters.answer_evaluation import create_openai_llm_call
from infrastructure.adapters.question_generation.llm.prompts import build_question_creation_prompt
from infrastructure.adapters.question_generation.llm.batch_prompts import build_batch_question_creation_prompt
from infrastructure.adapters.question_generation.llm.openai_client import create_openai_llm_call


@dataclass
class LLMQuestionGenerationService(QuestionGenerationService):
    """A question generation service that uses an LLM to generate questions."""
    client: object
    model: str = "gpt-4o"

    def __post_init__(self):
        """Initialize llm_call with the client."""
        self.llm_call = create_openai_llm_call(self.client, self.model)

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
            id=str(uuid.uuid4()),
            text=question_text,
            correct_answer=Answer(answer_text),
            difficulty=Difficulty(level=difficulty_level),
            knowledge_unit_id=ku.id
        )

        return question

    def generate_questions_batch(self, ku: KnowledgeUnit, count: int) -> list[Question]:
        """
        Generate multiple diverse questions for a KnowledgeUnit using an LLM.

        Parameters
        ----------
        ku : KnowledgeUnit
            The fact or skill to generate questions for.
        count : int
            Number of questions to generate.

        Returns
        -------
        list[Question]
        """
        # --- 1. Build batch prompt ---
        prompt = build_batch_question_creation_prompt(ku, count)

        # --- 2. Call the LLM ---
        raw_output = self.llm_call(prompt)

        # --- 3. Parse JSON output ---
        try:
            data = json.loads(raw_output)
            questions_data = data["questions"]
        except (json.JSONDecodeError, KeyError):
            # fallback: use single question generation
            return [self.generate_next_question(ku) for _ in range(count)]

        # --- 4. Construct Questions ---
        questions = []
        for q_data in questions_data[:count]:  # Ensure we don't exceed requested count
            try:
                question = Question(
                    id=str(uuid.uuid4()),
                    text=q_data["question_text"],
                    correct_answer=Answer(q_data["answer"]),
                    difficulty=Difficulty(level=q_data.get("difficulty_level", 2)),
                    knowledge_unit_id=ku.id
                )
                questions.append(question)
            except KeyError:
                # Skip malformed questions
                continue

        # If we didn't get enough valid questions, fill with single generations
        while len(questions) < count:
            questions.append(self.generate_next_question(ku))

        return questions