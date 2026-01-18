from dataclasses import dataclass

from domain.entities.learning import StudySession
from domain.entities.question import Question
from application.dto.study_session_view import StudySessionView
from application.dto.question_view import QuestionView
from domain.ports.question_repository import QuestionRepository


@dataclass
class StudySessionViewService:
    question_repository: QuestionRepository

    def build_view(self, session: StudySession) -> StudySessionView:
        questions = [
            self.question_repository.get_by_id(q_id)
            for q_id in session.questions
        ]

        question_views = [
            QuestionView(
                id=q.id,
                text=q.text,
                status=self._status(q),
                attempts=q.times_asked,
            )
            for q in questions
        ]

        completed = sum(q.status != "pending" for q in question_views)
        total = len(question_views)

        return StudySessionView(
            id=session.id,
            progress=completed / total if total else 0.0,
            questions=question_views,
            is_completed=session.is_completed(),
        )

    @staticmethod
    def _status(q: Question) -> str:
        if q.times_asked == 0:
            return "pending"
        if q.times_answered_correctly > 0:
            return "correct"
        return "incorrect"
