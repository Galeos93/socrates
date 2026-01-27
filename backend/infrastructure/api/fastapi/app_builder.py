from dataclasses import dataclass
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.api.fastapi.create_learning_plan_api import CreateLearningPlanAPIBase
from infrastructure.api.fastapi.get_learning_plan_api import GetLearningPlanAPIBase
from infrastructure.api.fastapi.start_study_session_api import StartStudySessionAPIBase
from infrastructure.api.fastapi.get_study_session_api import GetStudySessionAPIBase
from infrastructure.api.fastapi.submit_answer_api import SubmitAnswerAPIBase
from infrastructure.api.fastapi.assess_question_api import AssessQuestionAPIBase
from infrastructure.api.fastapi.update_mastery_api import UpdateMasteryAPIBase
from infrastructure.api.fastapi.ingest_document_api import IngestDocumentAPIBase
from infrastructure.api.fastapi.submit_feedback_api import SubmitFeedbackAPIBase


@dataclass
class AppBuilder:
    """FastAPI application builder for Socrates study assistant."""
    
    ingest_document_api: Optional[IngestDocumentAPIBase] = None
    create_learning_plan_api: Optional[CreateLearningPlanAPIBase] = None
    get_learning_plan_api: Optional[GetLearningPlanAPIBase] = None
    start_study_session_api: Optional[StartStudySessionAPIBase] = None
    get_study_session_api: Optional[GetStudySessionAPIBase] = None
    submit_answer_api: Optional[SubmitAnswerAPIBase] = None
    assess_question_api: Optional[AssessQuestionAPIBase] = None
    update_mastery_api: Optional[UpdateMasteryAPIBase] = None
    submit_feedback_api: Optional[SubmitFeedbackAPIBase] = None

    def register_document_routes(self, app: FastAPI) -> None:
        """Register document ingestion routes."""
        app.post("/documents")(self.ingest_document_api.ingest_document)

    def register_learning_plan_routes(self, app: FastAPI) -> None:
        """Register learning plan routes."""
        app.post("/learning-plans")(self.create_learning_plan_api.create_learning_plan)
        if self.get_learning_plan_api:
            app.get("/learning-plans/{learning_plan_id}")(self.get_learning_plan_api.get_learning_plan)

    def register_study_session_routes(self, app: FastAPI) -> None:
        """Register study session routes."""
        app.post("/learning-plans/{learning_plan_id}/sessions")(
            self.start_study_session_api.start_study_session
        )
        app.get("/learning-plans/{learning_plan_id}/sessions/{session_id}")(
            self.get_study_session_api.get_study_session
        )

    def register_health_routes(self, app: FastAPI) -> None:
        """Register health check routes."""
        @app.get("/health")
        def health_check():
            return {"status": "ok"}

    def register_answer_routes(self, app: FastAPI) -> None:
        """Register answer submission and assessment routes."""
        app.post("/learning-plans/{learning_plan_id}/sessions/{session_id}/answers/{question_id}")(
            self.submit_answer_api.submit_answer
        )
        app.post("/learning-plans/{learning_plan_id}/sessions/{session_id}/assess/{question_id}")(
            self.assess_question_api.assess_question
        )

    def register_mastery_routes(self, app: FastAPI) -> None:
        """Register mastery update routes."""
        app.post("/learning-plans/{learning_plan_id}/knowledge-units/{knowledge_unit_id}/mastery")(
            self.update_mastery_api.update_mastery
        )

    def register_feedback_routes(self, app: FastAPI) -> None:
        """Register feedback submission routes."""
        app.post("/learning-plans/{learning_plan_id}/sessions/{session_id}/feedback/{question_id}")(
            self.submit_feedback_api.submit_feedback
        )

    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI app with all registered use cases."""
        # Create the FastAPI instance
        app = FastAPI(
            title="Socrates Study Assistant",
            version="1.0.0",
            description="AI-powered study assistant using LLMs to generate knowledge units and questions",
        )

        # Register routes based on available APIs
        if self.ingest_document_api:
            self.register_document_routes(app)

        if self.create_learning_plan_api:
            self.register_learning_plan_routes(app)

        if self.start_study_session_api and self.get_study_session_api:
            self.register_study_session_routes(app)

        if self.submit_answer_api and self.assess_question_api:
            self.register_answer_routes(app)

        if self.update_mastery_api:
            self.register_mastery_routes(app)

        if self.submit_feedback_api:
            self.register_feedback_routes(app)

        self.register_health_routes(app)

        # Add CORS middleware (adjust for production)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            # allow_origins=["http://localhost:3000"],
            # allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        return app