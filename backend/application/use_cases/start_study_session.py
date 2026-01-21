from dataclasses import dataclass
from datetime import datetime, UTC
import itertools
import logging
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
        logging.info("[StartStudySessionUseCase] Starting new study session.")
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

        # 3. Generate questions using batch generation to avoid repetition
        questions: list[Question] = []
        
        # Calculate how many questions per KU
        questions_per_ku = self.max_questions // len(knowledge_units)
        remaining_questions = self.max_questions % len(knowledge_units)
        
        # Generate batch of questions for each KU
        for i, ku in enumerate(knowledge_units):
            # Distribute remaining questions to first KUs
            count = questions_per_ku + (1 if i < remaining_questions else 0)
            if count > 0:
                batch = self.question_generator.generate_questions_batch(ku, count)
                for question in batch:
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
