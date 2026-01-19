"""Shared fixtures for application-level tests."""
import uuid
import pytest
from typing import List
from datetime import datetime, UTC

from domain.entities.document import Document, DocumentID
from domain.entities.claim import Claim
from domain.entities.knowledge_unit import (
    KnowledgeUnit,
    FactKnowledge,
    SkillKnowledge,
    KnowledgeUnitID,
)
from domain.entities.question import Question, QuestionID, Difficulty, Answer
from domain.entities.learning import LearningPlan, StudySession, LearningPlanID


# ============================================================================
# Domain Entity Fixtures
# ============================================================================


@pytest.fixture
def sample_document() -> Document:
    """Provide a sample document for testing."""
    return Document(
        id=DocumentID("doc-1"),
        text="Python is a high-level programming language. It emphasizes code readability.",
    )


@pytest.fixture
def sample_claim(sample_document: Document) -> Claim:
    """Provide a sample claim for testing."""
    return Claim(
        text="Python is a high-level programming language.",
        doc_id=sample_document.id,
    )


@pytest.fixture
def sample_fact_knowledge(sample_claim: Claim) -> FactKnowledge:
    """Provide a sample fact knowledge unit."""
    return FactKnowledge(
        id=KnowledgeUnitID(str(uuid.uuid4())),
        description="Understanding that Python is high-level",
        target_claim=sample_claim,
        importance=0.8,
        mastery_level=0.0,
    )


@pytest.fixture
def sample_skill_knowledge(sample_claim: Claim) -> SkillKnowledge:
    """Provide a sample skill knowledge unit."""
    return SkillKnowledge(
        id=KnowledgeUnitID(str(uuid.uuid4())),
        description="Write a Python hello world program",
        source_claims=[sample_claim],
        importance=0.7,
        mastery_level=0.0,
    )


@pytest.fixture
def sample_knowledge_units(
    sample_fact_knowledge: FactKnowledge,
    sample_skill_knowledge: SkillKnowledge,
) -> List[KnowledgeUnit]:
    """Provide a list of sample knowledge units."""
    return [sample_fact_knowledge, sample_skill_knowledge]


@pytest.fixture
def sample_question(sample_fact_knowledge: FactKnowledge) -> Question:
    """Provide a sample question."""
    return Question(
        id=QuestionID(str(uuid.uuid4())),
        text="What type of language is Python?",
        difficulty=Difficulty(level=2),
        correct_answer=Answer("High-level programming language"),
        knowledge_unit_id=sample_fact_knowledge.id,
    )


@pytest.fixture
def sample_learning_plan(sample_knowledge_units: List[KnowledgeUnit]) -> LearningPlan:
    """Provide a sample learning plan."""
    return LearningPlan(
        id=LearningPlanID(str(uuid.uuid4())),
        knowledge_units=sample_knowledge_units,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_study_session(sample_learning_plan: LearningPlan) -> StudySession:
    """Provide a sample study session within a learning plan."""
    session = sample_learning_plan.start_session(max_questions=5)
    return session
