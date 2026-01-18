import json
from dataclasses import dataclass
from typing import Callable

from domain.ports.answer_evaluation import AnswerEvaluationService
from domain.entities.question import Question, Answer


@dataclass
class LLMAnswerEvaluationService(AnswerEvaluationService):
    """
    LLM-based implementation of AnswerEvaluationService.

    Uses an LLM to evaluate whether a user's answer is correct
    given the question and the expected answer.
    """

    llm_call: Callable[[str], str]

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
