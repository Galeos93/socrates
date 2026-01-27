from abc import ABC, abstractmethod

from domain.entities.question import AssessmentFeedback, QuestionFeedback


class AssessmentFeedbackService(ABC):
    """
    Port for assessment feedback services that track user feedback on assessments.
    
    Different implementations might:
    - Store feedback in a database
    - Send feedback to an observability platform (e.g., Opik)
    - Combine multiple tracking mechanisms
    """

    @abstractmethod
    def submit_feedback(self, feedback: AssessmentFeedback) -> None:
        """
        Submit user feedback for a question assessment.
        
        Parameters
        ----------
        feedback : AssessmentFeedback
            The assessment feedback to submit.
        """
        pass


class QuestionFeedbackService(ABC):
    """
    Port for question feedback services that track user feedback on question quality.
    
    Different implementations might:
    - Store feedback in a database
    - Send feedback to an observability platform (e.g., Opik)
    - Combine multiple tracking mechanisms
    """

    @abstractmethod
    def submit_feedback(self, feedback: QuestionFeedback) -> None:
        """
        Submit user feedback for question quality.
        
        Parameters
        ----------
        feedback : QuestionFeedback
            The question feedback to submit.
        """
        pass
