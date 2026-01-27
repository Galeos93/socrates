from dataclasses import dataclass
import logging
from typing import Optional

from opik import Opik
from opik.api_objects import trace_annotation

from domain.ports.feedback_service import AssessmentFeedbackService, QuestionFeedbackService
from domain.entities.question import AssessmentFeedback, QuestionFeedback


@dataclass
class OpikAssessmentFeedbackService(AssessmentFeedbackService):
    """
    Assessment feedback service that annotates Opik traces with user feedback.
    
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
        Submit assessment feedback by annotating the corresponding Opik trace.

        Parameters
        ----------
        feedback : AssessmentFeedback
            The assessment feedback to submit.
        """
        logging.info(
            f"[OpikAssessmentFeedbackService] Searching for assessment trace for question {feedback.question_id}"
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
                    f"[OpikAssessmentFeedbackService] No trace found for question {feedback.question_id}"
                )
                return

            target_trace = trace_list[0]
            logging.info(
                f"[OpikAssessmentFeedbackService] Found trace {target_trace.id}, annotating with assessment feedback"
            )

            # Create annotation with feedback
            annotation = trace_annotation.TraceAnnotation(
                trace_id=target_trace.id,
                name="assessment_feedback",
                value=feedback.score,
                reason=feedback.comment,
            )

            # Submit the annotation
            self.opik_client.annotate_trace(annotation)

            logging.info(
                f"[OpikAssessmentFeedbackService] Successfully annotated trace {target_trace.id} "
                f"with score {feedback.score}"
            )

        except Exception as e:
            logging.error(
                f"[OpikAssessmentFeedbackService] Error submitting assessment feedback: {str(e)}",
                exc_info=True,
            )
            # Don't raise - feedback submission should not break the main flow


@dataclass
class OpikQuestionFeedbackService(QuestionFeedbackService):
    """
    Question feedback service that annotates Opik traces with user feedback.
    
    This implementation:
    1. Searches for the question generation trace using metadata filters
    2. Annotates the trace with user feedback
    """

    opik_client: Optional[Opik] = None

    def __post_init__(self):
        """Initialize Opik client if not provided."""
        if self.opik_client is None:
            self.opik_client = Opik()

    def submit_feedback(self, feedback: QuestionFeedback) -> None:
        """
        Submit question feedback by annotating the corresponding Opik trace.

        Parameters
        ----------
        feedback : QuestionFeedback
            The question feedback to submit.
        """
        logging.info(
            f"[OpikQuestionFeedbackService] Searching for question generation trace for question {feedback.question_id}"
        )

        try:
            # Search for traces matching the question generation context
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
                    f"[OpikQuestionFeedbackService] No trace found for question {feedback.question_id}"
                )
                return

            target_trace = trace_list[0]
            logging.info(
                f"[OpikQuestionFeedbackService] Found trace {target_trace.id}, annotating with question feedback"
            )

            # Create annotation with feedback
            annotation = trace_annotation.TraceAnnotation(
                trace_id=target_trace.id,
                name="question_feedback",
                value=1 if feedback.is_helpful else 0,
                reason="User found question helpful" if feedback.is_helpful else "User did not find question helpful",
            )

            # Submit the annotation
            self.opik_client.annotate_trace(annotation)

            logging.info(
                f"[OpikQuestionFeedbackService] Successfully annotated trace {target_trace.id} "
                f"with is_helpful={feedback.is_helpful}"
            )

        except Exception as e:
            logging.error(
                f"[OpikQuestionFeedbackService] Error submitting question feedback: {str(e)}",
                exc_info=True,
            )
            # Don't raise - feedback submission should not break the main flow

            f"[OpikFeedbackService] Searching for question trace for question {feedback.question_id}"
        )

        try:
            # Search for traces matching the question context
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
                f"[OpikFeedbackService] Found trace {target_trace.id}, annotating with question feedback"
            )

            # Create annotation with feedback (1 for helpful, 0 for not helpful)
            annotation = trace_annotation.TraceAnnotation(
                trace_id=target_trace.id,
                name="question_feedback",
                value=1 if feedback.is_helpful else 0,
                reason="helpful" if feedback.is_helpful else "not_helpful",
            )

            # Submit the annotation
            self.opik_client.annotate_trace(annotation)

            logging.info(
                f"[OpikFeedbackService] Successfully annotated trace {target_trace.id} "
                f"with helpfulness: {feedback.is_helpful}"
            )

        except Exception as e:
            logging.error(
                f"[OpikFeedbackService] Error submitting question feedback: {str(e)}",
                exc_info=True,
            )
            # Don't raise - feedback submission should not break the main flow
