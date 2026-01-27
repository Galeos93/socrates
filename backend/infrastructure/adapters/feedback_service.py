from dataclasses import dataclass
import logging
from typing import Optional

from opik import Opik
from opik.api_objects import trace_annotation

from domain.ports.feedback_service import FeedbackService
from domain.entities.question import AssessmentFeedback


@dataclass
class OpikFeedbackService(FeedbackService):
    """
    Feedback service that annotates Opik traces with user feedback.
    
    This implementation:
    1. Searches for the assessment trace using metadata filters
    2. Annotates the trace with user feedback
    """

    opik_client: Optional[Opik] = None

    def __post_init__(self):
        """Initialize Opik client if not provided."""
        if self.opik_client is None:
            self.opik_client = Opik()

    def submit_feedback(self, feedback: AssessmentFeedback) -> None:
        """
        Submit feedback by annotating the corresponding Opik trace.

        Parameters
        ----------
        feedback : AssessmentFeedback
            The feedback to submit.
        """
        logging.info(
            f"[OpikFeedbackService] Searching for trace for question {feedback.question_id}"
        )

        try:
            # Search for traces matching the assessment context
            traces = self.opik_client.search_traces(
                project_name=None,  # Use default project
                filter_string=(
                    f'metadata.learning_plan_id = "{feedback.learning_plan_id}" '
                    f'AND metadata.study_session_id = "{feedback.session_id}" '
                    f'AND metadata.question_id = "{feedback.question_id}"'
                ),
            )

            # Get the first (most recent) matching trace
            trace_list = list(traces)
            if not trace_list:
                logging.warning(
                    f"[OpikFeedbackService] No trace found for question {feedback.question_id}"
                )
                return

            target_trace = trace_list[0]
            logging.info(
                f"[OpikFeedbackService] Found trace {target_trace.id}, annotating with feedback"
            )

            # Create annotation with feedback
            annotation = trace_annotation.TraceAnnotation(
                trace_id=target_trace.id,
                name="user_feedback",
                value=feedback.score,
                reason=feedback.comment,
            )

            # Submit the annotation
            self.opik_client.annotate_trace(annotation)

            logging.info(
                f"[OpikFeedbackService] Successfully annotated trace {target_trace.id} "
                f"with score {feedback.score}"
            )

        except Exception as e:
            logging.error(
                f"[OpikFeedbackService] Error submitting feedback: {str(e)}",
                exc_info=True,
            )
            # Don't raise - feedback submission should not break the main flow
