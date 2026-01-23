from abc import ABC, abstractmethod
from dataclasses import dataclass

from opik import opik_context
from vyper import v

from application.use_cases.assess_question import AssessQuestionOutcomeUseCase
from domain.entities.question import AnswerAssessment

# TODO: Convert response into DTO
class AssessQuestionAPIBase(ABC):
    """Abstract base class for assessing question endpoints."""

    @abstractmethod
    async def assess_question(
        self,
        learning_plan_id: str,
        session_id: str,
        question_id: str,
    ) -> dict:
        """Assess a question answer."""
        pass


@dataclass
class AssessQuestionAPIImpl(AssessQuestionAPIBase):
    """Implementation of the AssessQuestionAPIBase."""
    assess_question_use_case: AssessQuestionOutcomeUseCase

    async def assess_question(
        self,
        learning_plan_id: str,
        session_id: str,
        question_id: str,
    ) -> dict:
        """Assess question endpoint implementation."""
        answer_assessment: AnswerAssessment = self.assess_question_use_case.execute(
            learning_plan_id=learning_plan_id,
            study_session_id=session_id,
            question_id=question_id,
        )

        if v.get_bool("opik.enable_tracking"):
            opik_context.update_current_trace(
                thread_id=learning_plan_id,
                tags=["study_session_assessment"],
                metadata={
                    "learning_plan_id": learning_plan_id,
                    "study_session_id": session_id,
                    "question_id": question_id,
                    "is_correct": answer_assessment.is_correct,
                },
            )

        return {
            "is_correct": answer_assessment.is_correct,
            "correct_answer": answer_assessment.correct_answer,
            "explanation": answer_assessment.explanation,
            "question_id": question_id,
        }
