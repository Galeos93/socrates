import dataclass


@dataclass(frozen=True)
class QuestionView:
    id: str
    text: str
    status: str  # pending | correct | incorrect
    attempts: int
