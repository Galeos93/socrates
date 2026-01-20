import json
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Callable

from openai import OpenAI

from domain.ports.answer_evaluation import AnswerEvaluationService
from domain.entities.question import Question, Answer, AnswerAssessment


def create_openai_llm_call(
    client: OpenAI,
    model: str = "gpt-4o",
) -> Callable[[str], str]:
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
    """LLM-based implementation of AnswerEvaluationService.

    Notes
    -----
    Produces a rich AssessmentResult, including optional explanation.
    """

    client: OpenAI
    model: str = "gpt-4o"

    def __post_init__(self) -> None:
        self.llm_call = create_openai_llm_call(self.client, self.model)

    def evaluate(
        self,
        question: Question,
        user_answer: Answer,
    ) -> AnswerAssessment:
        prompt = self._build_prompt(question, user_answer)
        raw_response = self.llm_call(prompt)

        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError:
            # Fail closed
            return AnswerAssessment(
                is_correct=False,
                correct_answer=question.correct_answer,
                explanation=None,
                assessed_at=datetime.now(UTC),
            )

        return AnswerAssessment(
            is_correct=bool(data.get("is_correct", False)),
            correct_answer=question.correct_answer,
            explanation=data.get("explanation"),
            assessed_at=datetime.now(UTC),
        )

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

Respond ONLY with valid JSON in the following format, DO NOT enclose it with
``json`` or any other markdown:

{{
  "is_correct": true | false,
  "explanation": "Brief explanation of why the answer is correct or incorrect"
}}
""".strip()
