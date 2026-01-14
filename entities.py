"""
Knowledge and Question Models for Learning System

This module defines the core data structures for a study system that
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
from abc import ABC, abstractmethod
import json
import os
from typing import Callable, NewType, List, Optional, Dict, Any
from dataclasses import dataclass, field
import uuid

from openai import OpenAI

# Type aliases for clarity
DocLocation = NewType("DocLocation", str)
DocumentID = NewType("DocumentID", str)
Answer = NewType("Answer", str)


@dataclass
class Difficulty:
    """Represents the difficulty level of a question."""
    level: int  # e.g., 1 to 5
    description: Optional[str] = ""


@dataclass
class Claim:
    """A discrete piece of knowledge extracted from a text that can be directly
    or indirectly verified using the text itself."""
    text: str
    doc_id: DocumentID
    doc_location: Optional[DocLocation] = None  # e.g., character range or paragraph ID


@dataclass(kw_only=True)
class KnowledgeUnit:
    """A base class for knowledge units (claims or skills)."""
    id: str
    mastery_level: float = field(default=0.0)  # 0.0 to 1.0


@dataclass(kw_only=True)
class SkillKnowledge(KnowledgeUnit):
    """Knowledge about a skill derived from one or more claims."""
    source_claims: List[Claim]
    description: str


@dataclass(kw_only=True)
class FactKnowledge(KnowledgeUnit):
    """Knowledge about a document claim."""
    description: str
    target_claim: Claim

@dataclass
class Question:
    """
    A question designed to test fact comprehension or skill application.

    Attributes
    ----------
    text : str
        The text of the question.
    difficulty : Difficulty
        Difficulty level of the question.
    answer : Answer
        Correct answer.
    knowledge_unit : KnowledgeUnit
        The associated knowledge unit (FactKnowledge or SkillKnowledge).
    times_asked : int, optional
        Number of times the question has been asked. Default is 0.
    times_answered_correctly : int, optional
        Number of times the question has been answered correctly. Default is 0.
    """
    text: str
    difficulty: Difficulty
    answer: Answer
    knowledge_unit: KnowledgeUnit
    times_asked: int = 0
    times_answered_correctly: int = 0
    last_time_asked: Optional[str] = None  # ISO formatted datetime string


class KnowledgeUnitGenerationService(ABC):
    @abstractmethod
    def generate_knowledge_unit(
        self,
        text: str,
    ) -> list[KnowledgeUnit]:
        """Generate a KnowledgeUnit from text.

        Parameters
        ----------
        text: str
            The text to generate the KnowledgeUnits from.

        Returns
        -------
        list[KnowledgeUnit]

        """
        pass


class QuestionGenerationService(ABC):
    @abstractmethod
    def generate_next_question(
        self,
        ku: KnowledgeUnit
    ) -> Question:
        """Generate a question for a KnowledgeUnit.

        Parameters
        ----------
        ku: KnowledgeUnit
            The fact or skill to generate a question for.

        Returns
        -------
        Question
        """
        pass


class MasteryService(ABC):
    @abstractmethod
    def update_mastery(
        self,
        ku: KnowledgeUnit,
        questions: List[Question]
    ) -> KnowledgeUnit:
        """
        Update the mastery level of a KnowledgeUnit based on question performance.

        Parameters
        ----------
        ku: KnowledgeUnit
            The fact or skill to update mastery for.
        questions: List[Question]
            List of questions answered related to the KnowledgeUnit.

        Returns
        -------
        KnowledgeUnit

        """
        pass


class QuestionBasedMasteryService(MasteryService):

    @staticmethod
    def compute_mastery_from_questions(questions: List[Question]) -> float:
        if not questions:
            return 0.0

        total = 0.0
        weight_sum = 0.0

        for q in questions:
            if q.times_asked == 0:
                continue

            accuracy = q.times_answered_correctly / q.times_asked
            weight = q.difficulty.level

            total += accuracy * weight
            weight_sum += weight

        return min(1.0, total / weight_sum) if weight_sum > 0 else 0.0

    def calculate_mastery_from_questions(
        self,
        ku: KnowledgeUnit,
        questions: List[Question]
    ) -> float:
        """
        Calculate mastery level from question performance.

        Parameters
        ----------
        ku: KnowledgeUnit
            The fact or skill to calculate mastery for.
        questions: List[Question]
            List of questions answered related to the KnowledgeUnit.

        Returns
        -------
        float
            New mastery level between 0.0 and 1.0.
        """
        return self.compute_mastery_from_questions(questions)
    

class LLMKnowledgeUnitGenerationService(KnowledgeUnitGenerationService):
    """A knowledge unit generation service that uses an LLM to generate knowledge units."""
    # Generate a knowledge unit from text using an LLM.
    def generate_knowledge_unit(
        self,
        text: str,
    ) -> list[KnowledgeUnit]:
        # Placeholder implementation
        return FactKnowledge(
            id="fact1",
            text=text,
            description="Generated fact knowledge"
        )


class LLMQuestionGenerationService(QuestionGenerationService):
    """A question generation service that uses an LLM to generate questions."""

    def __init__(self, llm_call: Callable[[str], str]):
        """
        Parameters
        ----------
        llm_call : Callable[[str], str]
            A function that takes a prompt string and returns the LLM's raw text output.
        """
        self.llm_call = llm_call

    def generate_next_question(self, ku: KnowledgeUnit) -> Question:
        """
        Generate a question for a KnowledgeUnit using an LLM.

        Parameters
        ----------
        ku : KnowledgeUnit
            The fact or skill to generate a question for.

        Returns
        -------
        Question
        """
        # --- 1. Build prompt based on KnowledgeUnit type ---
        if isinstance(ku, FactKnowledge):
            source_texts = ku.target_claim.text
            prompt = f"""
            Generate a concise question to test comprehension of the following fact:

            Fact: {ku.description}
            Source Claim: {source_texts}

            Output JSON format only:
            {{
                "question_text": "string",
                "answer": "string",
                "difficulty_level": 1-5
            }}
            """
        elif isinstance(ku, SkillKnowledge):
            claims_texts = " ; ".join(c.text for c in ku.source_claims)
            prompt = f"""
            Generate a concise applied question to test the following skill:

            Skill: {ku.description}
            Source Claims: {claims_texts}

            Output JSON format only:
            {{
                "question_text": "string",
                "answer": "string",
                "difficulty_level": 1-5
            }}
            """
        else:
            raise ValueError(f"Unknown KnowledgeUnit type: {type(ku)}")

        # --- 2. Call the LLM ---
        raw_output = self.llm_call(prompt)

        # --- 3. Parse JSON output ---
        import json
        try:
            data = json.loads(raw_output)
            question_text = data["question_text"]
            answer_text = data["answer"]
            difficulty_level = data.get("difficulty_level", 2)  # default 2 if missing
        except (json.JSONDecodeError, KeyError):
            # fallback if LLM output fails
            question_text = ku.description
            answer_text = ku.target_claim.text if isinstance(ku, FactKnowledge) else "Answer TBD"
            difficulty_level = 2

        # --- 4. Construct Question ---
        question = Question(
            text=question_text,
            answer=Answer(answer_text),
            difficulty=Difficulty(level=difficulty_level),
            knowledge_unit=ku
        )

        return question


@dataclass
class Document:
    id: DocumentID
    text: str
    metadata: Optional[dict] = None  # e.g., title, author, date
    layout: Optional[Any] = None  # optional layout info, paragraphs, etc.


def openai_llm_call(prompt: str, model: str = "gpt-4", temperature: float = 0.0, max_tokens: int = 1000) -> str:
    """
    Calls the OpenAI API with a system + user message setup for consistent structured output.

    Parameters
    ----------
    prompt : str
        The text prompt containing instructions and one-shot examples.
    model : str
        The OpenAI model to use.
    temperature : float
        Sampling temperature. Set to 0 for deterministic output.
    max_tokens : int
        Maximum tokens to return.

    Returns
    -------
    str
        The LLM's raw text output (expected to be JSON).
    """
    client = OpenAI(
    # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a precise knowledge extraction assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # The assistant's message is in response.choices[0].message.content
    return response.choices[0].message.content.strip()


@dataclass
class LLMKnowledgeUnitGenerationService:
    llm_call: Callable[[str], str] = openai_llm_call

    def generate_knowledge_units(self, doc: Document) -> List[KnowledgeUnit]:
        """
        Generates KnowledgeUnits from a Document.

        Depending on implementation, claims may be anchored to:
        - Whole document
        - Paragraphs
        - Character ranges
        """
        prompt = self._build_prompt(doc)
        raw_response = self.llm_call(prompt)
        data = json.loads(raw_response)

        # --- Phase A: create claims ---
        claim_registry: Dict[int, Claim] = {}
        for item in data.get("claims", []):
            claim_registry[item["id"]] = Claim(
                text=item["text"],
                doc_id=doc.id,
            )

        # --- Phase B & C: Facts and Skills ---
        results: List[KnowledgeUnit] = []

        for item in data.get("facts", []):
            target_claim = claim_registry[item["target_claim_id"]]
            fact = FactKnowledge(
                id=str(uuid.uuid4()),
                description=item["description"],
                target_claim=target_claim
            )
            results.append(fact)

        for item in data.get("skills", []):
            source_claims = [claim_registry[i] for i in item["source_claim_ids"]]
            skill = SkillKnowledge(
                id=str(uuid.uuid4()),
                description=item["description"],
                source_claims=source_claims
            )
            results.append(skill)

        return results

    def _build_prompt(self, text: str) -> str:
        """
        Build the prompt for the LLM, including a one-shot example.
        """
        return f"""
You are an expert at reading a text and breaking it down into discrete, verifiable claims and knowledge units.

You will extract three types of information:

1. Claims: Atomic statements from the text that can be verified or inferred. Assign each a unique integer ID.
2. Facts: Declarative knowledge units based on exactly one claim (target claim).
3. Skills: Applied/procedural knowledge units based on one or more claims.

Your output must be strictly JSON in the following format:

{{
  "claims": [
    {{"id": 1, "text": "..."}},
    {{"id": 2, "text": "..."}}
  ],
  "facts": [
    {{"description": "...", "target_claim_id": 1}},
    {{"description": "...", "target_claim_id": 2}}
  ],
  "skills": [
    {{"description": "...", "source_claim_ids": [1,2]}},
    {{"description": "...", "source_claim_ids": [3]}}
  ]
}}

---

Example:

TEXT:
"To bake a sourdough loaf, you must first feed your starter to ensure it is active. 
Fermentation occurs because wild yeast consumes sugars and releases carbon dioxide. 
Once the dough has risen, bake it at 450°F. High heat gives the bread its airy structure."

OUTPUT:

{{
  "claims": [
    {{"id": 1, "text": "The sourdough starter must be fed before baking to ensure it is active."}},
    {{"id": 2, "text": "Fermentation occurs when wild yeast consumes sugars and releases carbon dioxide."}},
    {{"id": 3, "text": "Dough rises as a result of fermentation."}},
    {{"id": 4, "text": "Bake the dough at 450°F after it has risen."}},
    {{"id": 5, "text": "High baking heat is essential for proper oven spring."}},
    {{"id": 6, "text": "Oven spring gives bread its airy structure."}}
  ],
  "facts": [
    {{"description": "Feeding the starter ensures it is active and ready for baking.", "target_claim_id": 1}},
    {{"description": "Fermentation causes the dough to rise.", "target_claim_id": 3}},
    {{"description": "Baking at high temperature produces proper oven spring and airy bread.", "target_claim_id": 5}}
  ],
  "skills": [
    {{"description": "Prepare an active sourdough starter before baking.", "source_claim_ids": [1,2]}},
    {{"description": "Manage fermentation to ensure dough rises properly.", "source_claim_ids": [2,3]}},
    {{"description": "Bake sourdough at high temperature to achieve proper oven spring.", "source_claim_ids": [4,5,6]}}
  ]
}}

---

Now generate Claims, Facts, and Skills for the following text.
Return **only JSON**, do not include explanations:

TEXT:
"{text}"
"""
