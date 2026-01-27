from abc import ABC, abstractmethod

from domain.entities.question import AssessmentFeedback


class FeedbackService(ABC):
    """
    Port for feedback services that track user feedback on assessments.
    
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
            The feedback to submit.
        """
        pass
