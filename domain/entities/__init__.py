"""
Entities for Learning System

This package defines the core data structures for a study system that
supports both claim comprehension and skill application.

Classes:
--------
- Claim: A discrete piece of knowledge extracted from a document.
- KnowledgeUnit: Base class for knowledge objects.
- FactKnowledge: Knowledge derived directly from document claims.
- SkillKnowledge: Knowledge about a skill derived from one or more claims.
- Difficulty: Represents difficulty level for questions.
- Question: A question testing either fact comprehension or skill application.

Type aliases:
------------
- DocReference: str, reference to a document.
- Answer: str, the correct answer for a question.

Examples:
---------
# Creating a claim
claim1 = Claim(
    text="Words stressed on the final syllable ending in n or s carry an accent.",
    doc_reference="doc1"
)

# Fact knowledge derived from the claim
fact_knowledge = FactKnowledge(
    id="fact1",
    text=claim1.text,
    description="Accent rules",
    source_claims=[claim1]
)

# Skill knowledge derived from the claim
skill_knowledge = SkillKnowledge(
    id="skill1",
    name="Apply Spanish accent rules",
    description="Add accents according to stress rules",
    source_claims=[claim1],
    target_claim=claim1
)

# Claim comprehension question
q1 = Question(
    text="Which words require an accent according to the text?",
    difficulty=Difficulty(level=2, description="Basic comprehension"),
    answer=Answer("Words stressed on the final syllable ending in n or s"),
    knowledge_unit=fact_knowledge
)

# Skill application question
q2 = Question(
    text="Add the correct accent to 'corazón'.",
    difficulty=Difficulty(level=3, description="Applies accent rules"),
    answer=Answer("corazón"),
    knowledge_unit=skill_knowledge
)

"""