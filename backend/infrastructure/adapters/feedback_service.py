from dataclasses import dataclass, field
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
                    f'AND metadata.question_id = "{feedback.question_id}" '
                    f'AND tags contains "study_session_assessment"'
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
    1. Accumulates feedback per session (since one trace generates all questions)
    2. Updates the session trace with the mean feedback score
    3. Clears old session data when a new session is detected
    """

    opik_client: Optional[Opik] = None

    # In-memory storage: {session_id: {question_id: is_helpful}}
    _session_feedback: dict[str, dict[str, bool]] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize Opik client if not provided."""
        if self.opik_client is None:
            self.opik_client = Opik()

    def submit_feedback(self, feedback: QuestionFeedback) -> None:
        """
        Submit question feedback by annotating the corresponding Opik trace.

        Accumulates feedback per session and updates the trace with mean score.

        Parameters
        ----------
        feedback : QuestionFeedback
            The question feedback to submit.
        """
        session_id = feedback.session_id
        question_id = str(feedback.question_id)

        # Clear old sessions (keep only the last 10 sessions to prevent memory leak)
        if len(self._session_feedback) > 10:
            oldest_session = next(iter(self._session_feedback))
            logging.info(
                f"[OpikQuestionFeedbackService] Clearing old session {oldest_session} from memory"
            )
            del self._session_feedback[oldest_session]

        # Initialize session if not exists
        if session_id not in self._session_feedback:
            logging.info(
                f"[OpikQuestionFeedbackService] Starting feedback tracking for session {session_id}"
            )
            self._session_feedback[session_id] = {}

        # Store feedback for this question
        self._session_feedback[session_id][question_id] = feedback.is_helpful

        # Calculate mean feedback for the session
        feedbacks = list(self._session_feedback[session_id].values())
        helpful_count = sum(1 for f in feedbacks if f)
        mean_score = helpful_count / len(feedbacks) if feedbacks else 0.0

        logging.info(
            f"[OpikQuestionFeedbackService] Session {session_id}: {helpful_count}/{len(feedbacks)} questions rated helpful (mean={mean_score:.2f})"
        )

        try:
            # Search for the session trace (one trace per session, not per question)
            traces = self.opik_client.search_traces(
                project_name=v.get_string("opik.project_name"),
                filter_string=(
                    f'metadata.learning_plan_id = "{feedback.learning_plan_id}" '
                    f'AND metadata.study_session_id = "{session_id}" '
                    f'AND tags contains "study_session_retrieval"'
                ),
            )

            # Get the first (most recent) matching trace
            trace_list = list(traces)
            if not trace_list:
                logging.warning(
                    f"[OpikQuestionFeedbackService] No trace found for session {session_id}"
                )
                return

            target_trace = trace_list[0]
            logging.info(
                f"[OpikQuestionFeedbackService] Found session trace {target_trace.id}, updating with mean feedback"
            )

            # Log mean feedback score for the session
            self.opik_client.log_traces_feedback_scores(
                scores=[
                    {
                        "id": target_trace.id,
                        "name": "questions_quality",
                        "value": mean_score,
                        "reason": f"{helpful_count} out of {len(feedbacks)} questions rated helpful",
                    }
                ]
            )

            logging.info(
                f"[OpikQuestionFeedbackService] Successfully updated trace {target_trace.id} "
                f"with mean score {mean_score:.2f}"
            )

        except Exception as e:
            logging.error(
                f"[OpikQuestionFeedbackService] Error submitting question feedback: {str(e)}",
                exc_info=True,
            )
