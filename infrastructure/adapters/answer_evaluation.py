import json
from dataclasses import dataclass
from typing import Callable

from openai import OpenAI

from domain.ports.answer_evaluation import AnswerEvaluationService
from domain.entities.question import Question, Answer


def create_openai_llm_call(client: OpenAI, model: str = "gpt-4") -> Callable[[str], str]:
    """Create an llm_call function using the provided client and model."""
    def llm_call(prompt: str, temperature: float = 0.0) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise grading assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    return llm_call


@dataclass
class LLMAnswerEvaluationService(AnswerEvaluationService):
    """
    LLM-based implementation of AnswerEvaluationService.

    Uses an LLM to evaluate whether a user's answer is correct
    given the question and the expected answer.
    """

    client: object
    model: str = "gpt-4o"

    def __post_init__(self):
        """Initialize llm_call with the client."""
        from infrastructure.adapters.answer_evaluation import create_openai_llm_call
        self.llm_call = create_openai_llm_call(self.client, self.model)

    def evaluate(self, question: Question, user_answer: Answer) -> bool:
        prompt = self._build_prompt(question, user_answer)

        raw_response = self.llm_call(prompt)

        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError:
            # Fail closed: if the LLM response is invalid, mark as incorrect
            return False

        return bool(data.get("is_correct", False))

    def _build_prompt(self, question: Question, user_answer: Answer) -> str:
        return f"""
You are an automated grading system.

Evaluate whether the USER_ANSWER correctly answers the QUESTION.
Use the EXPECTED_ANSWER as the ground truth.

Be strict but fair.
Minor wording differences are acceptable if the meaning is correct.

QUESTION:
{question.text}

EXPECTED_ANSWER:
{question.correct_answer}

USER_ANSWER:
{user_answer}

Respond ONLY with valid JSON in the following format:

{{
  "is_correct": true | false
}}
""".strip()
