from dataclasses import dataclass

from domain.ports.question_repository import QuestionRepository
from domain.ports.answer_evaluation_service import AnswerEvaluationService
from domain.entities.question import Answer

@dataclass
class AssessQuestionOutcomeUseCase:
    """
    Determines whether an answer is correct and updates question stats.
    """

    question_repository: QuestionRepository
    # FIXME: To be implemented
    answer_evaluation_service: AnswerEvaluationService

    def execute(
        self,
        question_id: str,
        user_answer: Answer,
    ) -> bool:
        # 1. Load question
        question = self.question_repository.get_by_id(question_id)

        # 2. Evaluate correctness
        is_correct = self.answer_evaluation_service.evaluate(
            question=question,
            user_answer=user_answer,
        )

        # 3. Update stats
        if is_correct:
            question.times_answered_correctly += 1

        # 4. Persist
        self.question_repository.save(question)

        return is_correct