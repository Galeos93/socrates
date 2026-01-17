from domain.entities.knowledge_unit import KnowledgeUnit
from domain.entities.question import Question
from domain.ports.question_generation import QuestionGenerationService
from domain.ports.repositories.question_repository import QuestionRepository
from domain.services.mastery_service import MasteryService


class GenerateNextQuestionUseCase:
    def __init__(
        self,
        question_generator: QuestionGenerationService,
        mastery_service: MasteryService,
        question_repo: QuestionRepository,
    ):
        self.question_generator = question_generator
        self.mastery_service = mastery_service
        self.question_repo = question_repo

    def execute(self, ku: KnowledgeUnit) -> Question:
        question = self.question_generator.generate_next_question(ku)
        self.question_repo.save(question)
        return question
