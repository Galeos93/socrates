from dataclasses import dataclass
from datetime import datetime, UTC
import uuid

from domain.entities.learning import StudySession, LearningPlan
from domain.entities.question import Question, SessionQuestion
from domain.ports.question_generation import QuestionGenerationService
from domain.ports.study_focus_policy import StudyFocusPolicy
from domain.ports.learning_plan_repository import LearningPlanRepository
from domain.ports.question_repository import QuestionRepository


@dataclass
class StartStudySessionUseCase:
    """
    Creates a new StudySession for a LearningPlan.
    """

    learning_plan_repository: LearningPlanRepository
    study_focus_policy: StudyFocusPolicy
    question_generator: QuestionGenerationService
    question_repository: QuestionRepository

    max_questions: int = 5

    def execute(self, learning_plan_id: str) -> StudySession:
        # 1. Load learning plan
        learning_plan: LearningPlan = self.learning_plan_repository.get_by_id(
            learning_plan_id
        )

        # 2. Select knowledge units to study
        knowledge_units = self.study_focus_policy.select_knowledge_units(
            learning_plan.knowledge_units,
            max_units=3  # Example max_units, adjust as needed
        )

        # 3. Generate questions
        # FIXME: This could be optimized to batch generate questions
        # FIXME: More than one question per knowledge unit?
        questions: list[Question] = []
        for ku in knowledge_units:
            q: Question = self.question_generator.generate_next_question(ku)
            self.question_repository.save(q)
            questions.append(q)

        # 4. Create study session
        session = StudySession(
            id=str(uuid.uuid4()),
            knowledge_units=[ku.id for ku in knowledge_units],
            questions={q.id: SessionQuestion(question_id=q.id) for q in questions},
            max_questions=self.max_questions,
        )

        # 5. Persist session
        learning_plan.sessions.append(session)

        # 5. Persist aggregate
        self.learning_plan_repository.save(learning_plan)

        return session