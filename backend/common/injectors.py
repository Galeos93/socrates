"""Dependency injection container for Socrates application."""
import logging
from functools import partial

from openai import OpenAI
from opik import track
from opik.integrations.openai import track_openai
from vyper import v

# Domain services
from domain.services.mastery import QuestionBasedMasteryService

# Application services and use cases
from application.services.study_session_view import StudySessionViewService
from application.use_cases.assess_question import AssessQuestionOutcomeUseCase
from application.use_cases.create_learning_plan import (
    CreateLearningPlanFromDocumentUseCase,
)
from application.use_cases.document_ingestion import IngestDocumentUseCase
from application.use_cases.get_learning_plan import GetLearningPlanUseCase
from application.use_cases.get_study_session import GetStudySessionViewUseCase
from application.use_cases.start_study_session import StartStudySessionUseCase
from application.use_cases.submit_answer import SubmitAnswerUseCase
from application.use_cases.update_ku_mastery import UpdateKnowledgeUnitMasteryUseCase
from application.use_cases.submit_assessment_feedback import SubmitAssessmentFeedbackUseCase
from application.use_cases.submit_question_feedback import SubmitQuestionFeedbackUseCase

# Infrastructure adapters - Repositories
from infrastructure.adapters.document_repository import InMemoryDocumentRepository
from infrastructure.adapters.learning_plan_repository import (
    InMemoryLearningPlanRepository,
)
from infrastructure.adapters.question_repository import InMemoryQuestionRepository

# Infrastructure adapters - Policies
from infrastructure.adapters.learning_scope_policy import NaiveLearningScopePolicy
from infrastructure.adapters.study_focus_policy import WeightedStudyFocusPolicy

# Infrastructure adapters - Services
from infrastructure.adapters.answer_evaluation import LLMAnswerEvaluationService
from infrastructure.adapters.document_parser import LLMOCRDocumentParser
from infrastructure.adapters.feedback_service import (
    OpikAssessmentFeedbackService,
    OpikQuestionFeedbackService,
)
from infrastructure.adapters.knowledge_unit_generation.llm.service import (
    LLMKnowledgeUnitGenerationService,
)
from infrastructure.adapters.question_generation.llm.service import (
    LLMQuestionGenerationService,
)

# API implementations
from infrastructure.api.fastapi.assess_question_api import AssessQuestionAPIImpl
from infrastructure.api.fastapi.create_learning_plan_api import (
    CreateLearningPlanAPIImpl,
)
from infrastructure.api.fastapi.get_learning_plan_api import GetLearningPlanAPIImpl
from infrastructure.api.fastapi.get_study_session_api import GetStudySessionAPIImpl
from infrastructure.api.fastapi.ingest_document_api import IngestDocumentAPIBase
from infrastructure.api.fastapi.start_study_session_api import StartStudySessionAPIImpl
from infrastructure.api.fastapi.submit_answer_api import SubmitAnswerAPIImpl
from infrastructure.api.fastapi.update_mastery_api import UpdateMasteryAPIImpl
from infrastructure.api.fastapi.submit_assessment_feedback_api import SubmitAssessmentFeedbackAPIImpl
from infrastructure.api.fastapi.submit_question_feedback_api import SubmitQuestionFeedbackAPIImpl


# Singleton instances
_openai_client = None  # TODO: Maybe for the client we do not need singleton?
_document_repository = None
_learning_plan_repository = None
_question_repository = None


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        api_key = v.get_string("openai.api_key")
        if v.get_bool("opik.enable_tracking"):
            _openai_client = track_openai(OpenAI(api_key=api_key))
        else:
            _openai_client = OpenAI(api_key=api_key)
        logging.info("[Injector] OpenAI client initialized")
    return _openai_client


def get_document_repository() -> InMemoryDocumentRepository:
    """Get or create document repository instance."""
    global _document_repository
    if _document_repository is None:
        _document_repository = InMemoryDocumentRepository()
        logging.info("[Injector] Document repository initialized")
    return _document_repository


def get_learning_plan_repository() -> InMemoryLearningPlanRepository:
    """Get or create learning plan repository instance."""
    global _learning_plan_repository
    if _learning_plan_repository is None:
        _learning_plan_repository = InMemoryLearningPlanRepository(_plans={})
        logging.info("[Injector] Learning plan repository initialized")
    return _learning_plan_repository


def get_question_repository() -> InMemoryQuestionRepository:
    """Get or create question repository instance."""
    global _question_repository
    if _question_repository is None:
        _question_repository = InMemoryQuestionRepository(_questions={})
        logging.info("[Injector] Question repository initialized")
    return _question_repository


def get_document_parser() -> LLMOCRDocumentParser:
    """Create document parser instance."""
    client = get_openai_client()
    model = v.get_string("openai.vision_model")
    doc_parser = LLMOCRDocumentParser(client=client, model=model)
    if v.get_bool("opik.enable_tracking"):
        doc_parser.parse = track(doc_parser.parse)
    return doc_parser


def get_knowledge_unit_generator() -> LLMKnowledgeUnitGenerationService:
    """Create knowledge unit generation service instance."""
    client = get_openai_client()
    model = v.get_string("openai.completion_model")
    service = LLMKnowledgeUnitGenerationService(client=client, model=model)
    if v.get_bool("opik.enable_tracking"):
        service.generate_knowledge_units = partial(
            track(service.generate_knowledge_units),
            opik_args={
                "span": {
                    "tags": ["knowledge_unit_generation"],
                }
            }
        )
    return service


def get_question_generator() -> LLMQuestionGenerationService:
    """Create question generation service instance."""
    client = get_openai_client()
    model = v.get_string("openai.completion_model")
    service = LLMQuestionGenerationService(client=client, model=model)
    if v.get_bool("opik.enable_tracking"):
        # service.generate_questions_batch = track(service.generate_questions_batch)
        # service.generate_next_question = track(service.generate_next_question)
        service.generate_questions_batch = partial(
            track(service.generate_questions_batch),
            opik_args={
                "span": {
                    "tags": ["question_generation_batch"],
                }
            }
        )
        service.generate_next_question = partial(
            track(service.generate_next_question),
            opik_args={
                "span": {
                    "tags": ["question_generation_next"],
                }
            }
        )
    return service


def get_answer_evaluator() -> LLMAnswerEvaluationService:
    """Create answer evaluation service instance."""
    service = LLMAnswerEvaluationService(
        client=get_openai_client(),
        model=v.get_string("openai.completion_model"),
    )
    if v.get_bool("opik.enable_tracking"):
        # service.evaluate = track(service.evaluate)
        service.evaluate = partial(
            track(service.evaluate),
            opik_args={
                "span": {
                    "tags": ["answer_evaluation"],
                }
            }
        )
    return service

def get_learning_scope_policy() -> NaiveLearningScopePolicy:
    """Create learning scope policy instance."""
    return NaiveLearningScopePolicy()


def get_study_focus_policy() -> WeightedStudyFocusPolicy:
    """Create study focus policy instance."""
    return WeightedStudyFocusPolicy()


def get_mastery_service() -> QuestionBasedMasteryService:
    """Create mastery service instance."""
    return QuestionBasedMasteryService()


def get_assessment_feedback_service() -> OpikAssessmentFeedbackService:
    """Create assessment feedback service instance."""
    if v.get_bool("opik.enable_tracking"):
        return OpikAssessmentFeedbackService()
    else:
        # Return a no-op version if tracking is disabled
        from domain.ports.feedback_service import AssessmentFeedbackService
        from domain.entities.question import AssessmentFeedback
        
        class NoOpAssessmentFeedbackService(AssessmentFeedbackService):
            def submit_feedback(self, feedback: AssessmentFeedback) -> None:
                logging.info(f"[NoOpAssessmentFeedbackService] Feedback submission disabled: {feedback.id}")
        
        return NoOpAssessmentFeedbackService()


def get_question_feedback_service() -> OpikQuestionFeedbackService:
    """Create question feedback service instance."""
    if v.get_bool("opik.enable_tracking"):
        return OpikQuestionFeedbackService()
    else:
        # Return a no-op version if tracking is disabled
        from domain.ports.feedback_service import QuestionFeedbackService
        from domain.entities.question import QuestionFeedback
        
        class NoOpQuestionFeedbackService(QuestionFeedbackService):
            def submit_feedback(self, feedback: QuestionFeedback) -> None:
                logging.info(f"[NoOpQuestionFeedbackService] Feedback submission disabled: {feedback.id}")
        
        return NoOpQuestionFeedbackService()


def get_study_session_view_service() -> StudySessionViewService:
    """Create study session view service instance."""
    question_repo = get_question_repository()
    return StudySessionViewService(question_repository=question_repo)


# Use cases
def get_ingest_document_use_case() -> IngestDocumentUseCase:
    """Create ingest document use case instance."""
    return IngestDocumentUseCase(
        document_parser=get_document_parser(),
        document_repository=get_document_repository(),
    )


def get_create_learning_plan_use_case() -> CreateLearningPlanFromDocumentUseCase:
    """Create learning plan use case instance."""
    return CreateLearningPlanFromDocumentUseCase(
        ku_generator=get_knowledge_unit_generator(),
        learning_scope_policy=get_learning_scope_policy(),
        learning_plan_repository=get_learning_plan_repository(),
    )


def get_learning_plan_use_case() -> GetLearningPlanUseCase:
    """Create get learning plan use case instance."""
    return GetLearningPlanUseCase(
        learning_plan_repository=get_learning_plan_repository(),
    )


def get_start_study_session_use_case() -> StartStudySessionUseCase:
    """Create start study session use case instance."""
    max_questions = v.get_int("study_session.max_questions")
    return StartStudySessionUseCase(
        learning_plan_repository=get_learning_plan_repository(),
        study_focus_policy=get_study_focus_policy(),
        question_generator=get_question_generator(),
        question_repository=get_question_repository(),
        max_questions=max_questions,
    )


def get_get_study_session_use_case() -> GetStudySessionViewUseCase:
    """Create get study session use case instance."""
    return GetStudySessionViewUseCase(
        learning_plan_repo=get_learning_plan_repository(),
        view_service=get_study_session_view_service(),
    )


def get_submit_answer_use_case() -> SubmitAnswerUseCase:
    """Create submit answer use case instance."""
    return SubmitAnswerUseCase(
        learning_plan_repository=get_learning_plan_repository(),
    )


def get_assess_question_use_case() -> AssessQuestionOutcomeUseCase:
    """Create assess question use case instance."""
    return AssessQuestionOutcomeUseCase(
        learning_plan_repository=get_learning_plan_repository(),
        question_repository=get_question_repository(),
        answer_evaluation_service=get_answer_evaluator(),
    )


def get_update_mastery_use_case() -> UpdateKnowledgeUnitMasteryUseCase:
    """Create update mastery use case instance."""
    return UpdateKnowledgeUnitMasteryUseCase(
        learning_plan_repository=get_learning_plan_repository(),
        mastery_service=get_mastery_service(),
    )


def get_submit_assessment_feedback_use_case() -> SubmitAssessmentFeedbackUseCase:
    """Create submit assessment feedback use case instance."""
    return SubmitAssessmentFeedbackUseCase(
        feedback_service=get_assessment_feedback_service(),
    )


def get_submit_question_feedback_use_case() -> SubmitQuestionFeedbackUseCase:
    """Create submit question feedback use case instance."""
    return SubmitQuestionFeedbackUseCase(
        feedback_service=get_question_feedback_service(),
    )


# API implementations
def get_ingest_document_api() -> IngestDocumentAPIBase:
    """Create ingest document API instance."""
    api = IngestDocumentAPIBase(ingest_document_use_case=get_ingest_document_use_case())

    if v.get_bool("opik.enable_tracking"):
        api.ingest_document = track(api.ingest_document)

    return api


def get_create_learning_plan_api() -> CreateLearningPlanAPIImpl:
    """Create learning plan API instance."""
    api = CreateLearningPlanAPIImpl(
        create_learning_plan_use_case=get_create_learning_plan_use_case(),
        document_repository=get_document_repository(),
    )

    if v.get_bool("opik.enable_tracking"):
        api.create_learning_plan = track(api.create_learning_plan)

    return api


def get_learning_plan_api() -> GetLearningPlanAPIImpl:
    """Create get learning plan API instance."""
    return GetLearningPlanAPIImpl(
        get_learning_plan_use_case=get_learning_plan_use_case(),
    )


def get_start_study_session_api() -> StartStudySessionAPIImpl:
    """Create start study session API instance."""
    api = StartStudySessionAPIImpl(
        start_study_session_use_case=get_start_study_session_use_case()
    )

    if v.get_bool("opik.enable_tracking"):
        api.start_study_session = track(api.start_study_session)

    return api


def get_get_study_session_api() -> GetStudySessionAPIImpl:
    """Create get study session API instance."""
    return GetStudySessionAPIImpl(
        get_study_session_use_case=get_get_study_session_use_case()
    )


def get_submit_answer_api() -> SubmitAnswerAPIImpl:
    """Create submit answer API instance."""
    return SubmitAnswerAPIImpl(submit_answer_use_case=get_submit_answer_use_case())


def get_assess_question_api() -> AssessQuestionAPIImpl:
    """Create assess question API instance."""
    api = AssessQuestionAPIImpl(assess_question_use_case=get_assess_question_use_case())
    if v.get_bool("opik.enable_tracking"):
        api.assess_question = track(api.assess_question)
    return api


def get_update_mastery_api() -> UpdateMasteryAPIImpl:
    """Create update mastery API instance."""
    return UpdateMasteryAPIImpl(update_mastery_use_case=get_update_mastery_use_case())


def get_submit_assessment_feedback_api() -> SubmitAssessmentFeedbackAPIImpl:
    return SubmitAssessmentFeedbackAPIImpl(
        submit_assessment_feedback_use_case=get_submit_assessment_feedback_use_case(),
    )


def get_submit_question_feedback_api() -> SubmitQuestionFeedbackAPIImpl:
    return SubmitQuestionFeedbackAPIImpl(
        submit_question_feedback_use_case=get_submit_question_feedback_use_case(),
    )
