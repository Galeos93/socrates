from dataclasses import dataclass

from domain.entities.question import Question, Answer


class AnswerEvaluationService:
    """
    Service interface for evaluating the correctness of answers to questions.
    """

    def evaluate(self, question: Question, user_answer: Answer) -> bool:
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
        bool
            True if the answer is correct, False otherwise.
        """
        # Placeholder implementation; actual logic would depend on question type
        return question.correct_answer == user_answer
