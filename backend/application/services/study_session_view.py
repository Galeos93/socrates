from dataclasses import dataclass

from domain.entities.learning import StudySession
from domain.entities.question import Question, SessionQuestion, QuestionStatus
from application.dto.study_session_view import StudySessionView
from application.dto.question_view import QuestionView
from domain.ports.question_repository import QuestionRepository


@dataclass
class StudySessionViewService:
    question_repository: QuestionRepository

    def build_view(self, session: StudySession) -> StudySessionView:
        question_ids = [q_id for q_id in session.questions.keys()]
        session_questions: list[SessionQuestion] = session.questions.values()
        questions: list[Question] = [
            self.question_repository.get_by_id(q_id)
            for q_id in question_ids
        ]

        question_views = [
            QuestionView(
                id=question.id,
                text=question.text,
                status=self._status(session_question),
                attempts=session_question.attempts,
            )
            for session_question, question in zip(session_questions, questions)
        ]

        completed = sum(q.status != QuestionStatus.PENDING for q in question_views)
        total = len(question_views)

        return StudySessionView(
            id=session.id,
            progress=completed / total if total else 0.0,
            questions=question_views,
            is_completed=session.is_completed(),
        )

    @staticmethod
    def _status(q: SessionQuestion) -> QuestionStatus:
        if q.attempts == 0:
            return QuestionStatus.PENDING
        if q.is_correct:
            return QuestionStatus.CORRECT
        return QuestionStatus.INCORRECT
