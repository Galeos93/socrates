from dataclasses import dataclass

from domain.entities.question import Question
from application.dto.question_view import QuestionView, QuestionStatus


@dataclass
class QuestionViewService:
    def build(self, question: Question) -> QuestionView:
        if question.times_asked == 0:
            status = QuestionStatus.PENDING
        elif question.times_answered_correctly > 0:
            # FIXME: I disagree with this
            status = QuestionStatus.CORRECT
        else:
            status = QuestionStatus.INCORRECT

        return QuestionView(
            id=question.id,
            text=question.text,
            status=status,
            attempts=question.times_asked,
        )
