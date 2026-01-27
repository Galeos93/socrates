from dataclasses import dataclass
from typing import NewType

from domain.entities.question import QuestionID
from domain.entities.learning import LearningPlanID, StudySessionID


AssessmentID = NewType("AssessmentID", str)


@dataclass(frozen=True)
class SubmitAssessmentFeedbackDTO:
    """DTO for submitting feedback on answer assessments."""
    assessment_id: AssessmentID
    question_id: QuestionID
    learning_plan_id: LearningPlanID
    session_id: StudySessionID
    agrees: bool  # True = user agrees with assessment
    comment: str | None = None  # optional, expandable later


@dataclass(frozen=True)
class SubmitQuestionFeedbackDTO:
    """DTO for submitting feedback on question quality."""
    question_id: QuestionID
    learning_plan_id: LearningPlanID
    session_id: StudySessionID
    is_helpful: bool  # True = question was helpful
