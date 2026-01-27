from dataclasses import dataclass
import logging
from typing import Optional

from opik import Opik
from vyper import v

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
                project_name=v.get_string("opik.project_name"),  # Use configured project
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

            # Log feedback score using Opik API
            self.opik_client.log_traces_feedback_scores(
                scores=[
                    {
                        "id": target_trace.id,
                        "name": "assessment_feedback",
                        "value": feedback.score,
                        "reason": feedback.comment,
                    }
                ]
            )

            logging.info(
                f"[OpikAssessmentFeedbackService] Successfully logged feedback for trace {target_trace.id} "
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
                project_name=v.get_string("opik.project_name"),  # Use configured project
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

            # Log feedback score using Opik API
            self.opik_client.log_traces_feedback_scores(
                scores=[
                    {
                        "id": target_trace.id,
                        "name": "question_feedback",
                        "value": 1 if feedback.is_helpful else 0,
                        "reason": "User found question helpful" if feedback.is_helpful else "User did not find question helpful",
                    }
                ]
            )

            logging.info(
                f"[OpikQuestionFeedbackService] Successfully logged feedback for trace {target_trace.id} "
                f"with is_helpful={feedback.is_helpful}"
            )

        except Exception as e:
            logging.error(
                f"[OpikQuestionFeedbackService] Error submitting question feedback: {str(e)}",
                exc_info=True,
            )
