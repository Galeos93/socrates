from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.entities.question import Question, Answer, AnswerAssessment


@dataclass
class AnswerEvaluationService(ABC):
    """Service interface for evaluating the correctness of answers to questions."""

    @abstractmethod
    def evaluate(self, question: Question, user_answer: Answer) -> AnswerAssessment:
        """
        Evaluates whether the provided answer is correct for the given question.

        Parameters
        ----------
        question: Question
            The question to evaluate against.
        user_answer: Answer
            The answer provided by the user.

        Returns
        -------
        AnswerAssessment
            The assessment of the provided answer.
        """
        pass
