from dataclasses import dataclass
from datetime import datetime, UTC
import uuid
import itertools

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

    Hackathon version:
    - Focus policy selects candidate KnowledgeUnits
    - Questions are generated until max_questions is reached
    - KnowledgeUnits are reused (round-robin)
    """

    learning_plan_repository: LearningPlanRepository
    study_focus_policy: StudyFocusPolicy
    question_generator: QuestionGenerationService
    question_repository: QuestionRepository

    max_questions: int = 6
    max_knowledge_units: int = 3

    def execute(self, learning_plan_id: str) -> StudySession:
        # 1. Load learning plan
        learning_plan: LearningPlan | None = (
            self.learning_plan_repository.get_by_id(learning_plan_id)
        )
        if not learning_plan:
            raise ValueError("LearningPlan not found")

        # 2. Select focus knowledge units
        knowledge_units = self.study_focus_policy.select_knowledge_units(
            learning_plan.knowledge_units,
            max_units=self.max_knowledge_units,
        )

        if not knowledge_units:
            raise ValueError("No knowledge units selected for study session")

        # 3. Generate questions (round-robin over KUs)
        questions: list[Question] = []
        ku_cycle = itertools.cycle(knowledge_units)

        # TODO: This policy should be a class attribute
        while len(questions) < self.max_questions:
            ku = next(ku_cycle)
            question: Question = self.question_generator.generate_next_question(ku)
            self.question_repository.save(question)
            questions.append(question)

        # 4. Create study session
        session = StudySession(
            id=str(uuid.uuid4()),
            knowledge_units=[ku.id for ku in knowledge_units],
            questions={
                q.id: SessionQuestion(
                    question_id=q.id,
                    knowledge_unit_id=q.knowledge_unit_id,
                )
                for q in questions
            },
            max_questions=self.max_questions,
            started_at=datetime.now(tz=UTC),
        )

        # 5. Attach session to learning plan
        learning_plan.sessions.append(session)

        # 6. Persist aggregate root
        self.learning_plan_repository.save(learning_plan)

        return session
