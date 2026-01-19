from dataclasses import dataclass

from application.dto.question_view import QuestionView


@dataclass(frozen=True)
class StudySessionView:
    id: str
    progress: float
    questions: list[QuestionView]
    is_completed: bool
