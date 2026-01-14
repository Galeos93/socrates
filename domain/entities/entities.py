
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
