from dataclasses import dataclass


@dataclass(frozen=True)
class StudySessionView:
    id: str
    progress: float
    questions: list[QuestionView]
    is_completed: bool
