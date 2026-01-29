class LearningPlanNotFoundException(Exception):
    """Exception raised when a learning plan is not found."""
    def __init__(self, learning_plan_id: str):
        self.learning_plan_id = learning_plan_id
        super().__init__(f"Learning plan with ID '{learning_plan_id}' not found")


class StudySessionNotFoundException(Exception):
    """Exception raised when a study session is not found."""
    def __init__(self, study_session_id: str):
        self.study_session_id = study_session_id
        super().__init__(f"Study session with ID '{study_session_id}' not found")


class QuestionNotFoundException(Exception):
    """Exception raised when a question is not found."""
    def __init__(self, question_id: str):
        self.question_id = question_id
        super().__init__(f"Question with ID '{question_id}' not found")


class QuestionNotInStudySessionException(Exception):
    """Exception raised when a question is not part of the specified study session."""
    def __init__(self, question_id: str, study_session_id: str):
        self.question_id = question_id
        self.study_session_id = study_session_id
        super().__init__(f"Question '{question_id}' not part of study session '{study_session_id}'")


class KUNotInLearningPlanException(Exception):
    """Exception raised when a knowledge unit is not part of the learning plan."""
    def __init__(self, knowledge_unit_id: str, learning_plan_id: str):
        self.knowledge_unit_id = knowledge_unit_id
        self.learning_plan_id = learning_plan_id
        super().__init__(f"Knowledge unit '{knowledge_unit_id}' not part of learning plan '{learning_plan_id}'")


class KUNotGeneratedException(Exception):
    """Exception raised when a knowledge unit could not be generated."""
    pass


class KUNotSelectedException(Exception):
    """Exception raised when no knowledge units are selected for a study session."""
    pass


class NoUnassessedAnswerAttemptException(Exception):
    """Exception raised when no unassessed answer attempt is found."""
    def __init__(self, question_id: str):
        self.question_id = question_id
        super().__init__(f"No unassessed answer attempt found for question '{question_id}'")