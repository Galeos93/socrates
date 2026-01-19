from dataclasses import dataclass

from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository
from domain.ports.answer_evaluation import AnswerEvaluationService
from domain.entities.question import Answer, QuestionID
from domain.entities.learning import StudySessionID


@dataclass
class AssessQuestionOutcomeUseCase:
    """
    Determines whether an answer is correct and updates session-specific state.
    """

    learning_plan_repository: LearningPlanRepository
    question_repository: QuestionRepository
    answer_evaluation_service: AnswerEvaluationService

    def execute(
        self,
        learning_plan_id: str,
        study_session_id: StudySessionID,
        question_id: QuestionID,
        user_answer: Answer,
    ) -> bool:
        # 1. Load aggregate root
        learning_plan = self.learning_plan_repository.get_by_id(learning_plan_id)
        if not learning_plan:
            raise ValueError("LearningPlan not found")

        # 2. Locate study session
        session = next(
            (s for s in learning_plan.sessions if s.id == study_session_id),
            None
        )
        if not session:
            raise ValueError("StudySession not found")

        # 3. Locate session question
        session_question = session.questions.get(question_id)
        if not session_question:
            raise ValueError("Question not part of this StudySession")

        # 4. Load canonical question
        question = self.question_repository.get_by_id(question_id)
        if not question:
            raise ValueError("Question not found")

        # 5. Evaluate correctness
        is_correct = self.answer_evaluation_service.evaluate(
            question=question,
            user_answer=user_answer,
        )

        # 6. Update session-specific state
        session_question.mark_correctness(is_correct)

        # 7. Persist aggregate
        self.learning_plan_repository.save(learning_plan)

        return is_correct
