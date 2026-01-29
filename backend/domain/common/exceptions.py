class StudySessionFullException(Exception):
    """Exception raised when trying to add a study session to a full learning plan."""
    def __init__(self, study_session_id: str):
        self.study_session_id = study_session_id
        super().__init__(f"Study session '{study_session_id}' cannot accept more questions")

class LearningPlanIsAlreadyCompletedException(Exception):
    """Exception raised when trying to modify a completed learning plan."""
    def __init__(self, learning_plan_id: str):
        self.learning_plan_id = learning_plan_id
        super().__init__(f"Learning plan '{learning_plan_id}' is already completed")