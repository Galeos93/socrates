from dataclasses import dataclass, field
from typing import List, Optional, NewType
import uuid
from datetime import datetime, UTC

from domain.entities.knowledge_unit import KnowledgeUnit
from domain.entities.question import QuestionID


StudySessionID = NewType("StudySessionID", str)
LearningPlanID = NewType("LearningPlanID", str)


@dataclass
class StudySession:
    """
    A bounded learning interaction consisting of a finite number of questions.
    A StudySession always belongs to a LearningPlan.
    """
    id: StudySessionID
    knowledge_units: List[KnowledgeUnit]
    max_questions: int
    questions: List[QuestionID] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ended_at: Optional[datetime] = None

    def can_ask_more_questions(self) -> bool:
        return len(self.questions) < self.max_questions and self.ended_at is None

    def register_question(self, question_id: QuestionID) -> None:
        if not self.can_ask_more_questions():
            raise ValueError("StudySession cannot accept more questions")
        self.questions.append(question_id)

    def end(self) -> None:
        if self.ended_at is None:
            self.ended_at = datetime.now(UTC)

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
            raise ValueError("LearningPlan is already completed")

        session = StudySession(
            id=str(uuid.uuid4()),
            knowledge_units=self.knowledge_units,
            max_questions=max_questions
        )
        self.sessions.append(session)
        return session

    def all_questions(self) -> List[Question]:
        return [q for session in self.sessions for q in session.questions]

    def is_completed(self) -> bool:
        return self.completed_at is not None

    def complete(self) -> None:
        if not self.is_completed():
            self.completed_at = datetime.now(UTC)
