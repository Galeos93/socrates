from dataclasses import dataclass, field
from typing import List, Optional, NewType
import uuid
from datetime import datetime, UTC

from domain.entities.knowledge_unit import KnowledgeUnit, KnowledgeUnitID
from domain.entities.question import QuestionID, SessionQuestion
from domain.common.exceptions import (
    LearningPlanIsAlreadyCompletedException,
    StudySessionFullException,
)


StudySessionID = NewType("StudySessionID", str)
LearningPlanID = NewType("LearningPlanID", str)


@dataclass
class StudySession:
    """
    A bounded learning interaction consisting of a finite number of questions.
    Owned by a LearningPlan.
    """
    id: StudySessionID
    knowledge_units: list[KnowledgeUnitID]
    max_questions: int
    questions: dict[QuestionID, SessionQuestion] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None

    def can_ask_more_questions(self) -> bool:
        return len(self.questions) < self.max_questions and self.ended_at is None

    def register_question(self, question_id: QuestionID) -> None:
        if not self.can_ask_more_questions():
            raise StudySessionFullException(self.id)

        if question_id in self.questions:
            return  # idempotent

        self.questions[question_id] = SessionQuestion(question_id=question_id)

    def is_completed(self) -> bool:
        return self.ended_at is not None



@dataclass
class LearningPlan:
    """
    Represents a learner's intent to master a set of KnowledgeUnits over time.
    A LearningPlan owns multiple StudySessions.
    """
    id: LearningPlanID
    knowledge_units: List[KnowledgeUnit]
    sessions: List[StudySession] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def start_session(self, max_questions: int) -> StudySession:
        if self.is_completed():
            raise LearningPlanIsAlreadyCompletedException(self.id)

        session = StudySession(
            id=str(uuid.uuid4()),
            knowledge_units=self.knowledge_units,
            max_questions=max_questions
        )
        self.sessions.append(session)
        return session

    def all_questions(self) -> List[SessionQuestion]:
        return [q for session in self.sessions for q in session.questions.values()]

    def is_completed(self) -> bool:
        return self.completed_at is not None

    def complete(self) -> None:
        if not self.is_completed():
            self.completed_at = datetime.now(UTC)
