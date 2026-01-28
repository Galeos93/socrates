import json
from pydantic import BaseModel
from typing import Any

from opik.evaluation.metrics import base_metric, score_result
from opik.evaluation import models

class LLMJudgeBinaryResult(BaseModel):
    score: bool
    reason: str

class MetricScore(BaseModel):
    score: float
    reason: str

class KnowledgeUnitGenerationResult(BaseModel):
    KURelevance: MetricScore
    KUGrounding: MetricScore
    KUDiversity: MetricScore
    KUComplexity: MetricScore
    KURedundancy: MetricScore


class KnowledgeUnitGenerationRule(base_metric.BaseMetric):
    def __init__(self, name: str = "KnowledgeUnitGenerationRule", model_name: str = "gpt-4o"):
        super().__init__(name)
        self.llm_client = models.LiteLLMChatModel(model_name=model_name)
        self.system_prompt = """
DOMAIN:

@dataclass(kw_only=True)
class KnowledgeUnit:
    \"\"\"A base class for knowledge units (claims or skills).\"\"\"
    id: KnowledgeUnitID
    description: str
    importance: float = field(default=0.0)  # 0.0 to 1.0
    mastery_level: float = field(default=0.0)  # 0.0 to 1.0
    document_references: List[DocumentID] = field(default_factory=list)


@dataclass(kw_only=True)
class SkillKnowledge(KnowledgeUnit):
    \"\"\"Knowledge about a skill derived from one or more claims.\"\"\"
    source_claims: List[Claim]


@dataclass(kw_only=True)
class FactKnowledge(KnowledgeUnit):
    \"\"\"Knowledge about a document claim.\"\"\"
    target_claim: Claim

OUTPUT:

KURelevance. How useful are these KnowledgeUnits for learning the input material?
KUGrounding. Are claims fully supported by the input text (no hallucination)?
KUDiversity. Do the KnowledgeUnits cover distinct aspects of the input?
KUComplexity. Do some KnowledgeUnits require synthesis across multiple parts of the input?
KURedundancy. How much unnecessary repetition exists?
"""
        self.user_prompt_template = """You are an impartial AI judge.

You will be given an INPUT, consisting of text that may span multiple documents, and an OUTPUT, consisting of a list of KnowledgeUnits derived from that input.

Your task is to evaluate the quality of the OUTPUT given the INPUT.

Evaluate the OUTPUT along the following dimensions. Each dimension must be scored as a float between 0.0 and 1.0, where higher is better, except where explicitly noted.

### Evaluation Criteria

1. KURelevance
How useful and important are the KnowledgeUnits for understanding or learning the content of the INPUT?
- 1.0 = All KnowledgeUnits are clearly important and on-topic
- 0.0 = Mostly irrelevant or trivial KnowledgeUnits

2. KUGrounding (Hallucination Check)
To what extent are the KnowledgeUnits fully supported by the INPUT?
- 1.0 = All claims are explicitly or implicitly grounded in the INPUT
- 0.0 = Many claims are hallucinated or unsupported

3. KUDiversity
To what extent do the KnowledgeUnits cover different concepts, facts, or skills from the INPUT?
- 1.0 = KnowledgeUnits cover a wide range of distinct ideas
- 0.0 = KnowledgeUnits focus narrowly on the same idea

4. KUComplexity
To what extent do the KnowledgeUnits require synthesis or inference across multiple parts of the INPUT?
- 1.0 = Several KnowledgeUnits combine information from different sections or documents
- 0.0 = All KnowledgeUnits are simple, direct extractions

5. KURedundancy (Penalty)
To what extent do the KnowledgeUnits unnecessarily repeat the same information?
- 1.0 = No meaningful redundancy; each KnowledgeUnit adds new value
- 0.0 = Heavy duplication or paraphrasing without added value

### INPUT
{input}

### OUTPUT
{output}

Provide your evaluation as a JSON object with the following structure (no backticks):

{{
    "KURelevance": {{"score": <float between 0.0 and 1.0>, "reason": "<brief explanation>"}},
    "KUGrounding": {{"score": <float between 0.0 and 1.0>, "reason": "<brief explanation>"}},
    "KUDiversity": {{"score": <float between 0.0 and 1.0>, "reason": "<brief explanation>"}},
    "KUComplexity": {{"score": <float between 0.0 and 1.0>, "reason": "<brief explanation>"}},
    "KURedundancy": {{"score": <float between 0.0 and 1.0>, "reason": "<brief explanation>"}}
}}
"""

    def score(self, input: str, output: str, **ignored_kwargs: Any) -> list[score_result.ScoreResult]:
        """
        Score the quality of generated KnowledgeUnits.

        Args:
            input: The input text/documents.
            output: The generated KnowledgeUnits.
            **ignored_kwargs: Any additional keyword arguments.
        """
        # Construct the promptº
        user_prompt = self.user_prompt_template.format(input=input, output=output)

        # Generate and parse the response from the LLM
        response = self.llm_client.generate_string(
            input=user_prompt,
            response_format=KnowledgeUnitGenerationResult
        )
        response_dict = json.loads(response)

        # Return individual scores for each dimension
        return [
            score_result.ScoreResult(
                name="KURelevance",
                value=response_dict["KURelevance"]["score"],
                reason=response_dict["KURelevance"]["reason"]
            ),
            score_result.ScoreResult(
                name="KUGrounding",
                value=response_dict["KUGrounding"]["score"],
                reason=response_dict["KUGrounding"]["reason"]
            ),
            score_result.ScoreResult(
                name="KUDiversity",
                value=response_dict["KUDiversity"]["score"],
                reason=response_dict["KUDiversity"]["reason"]
            ),
            score_result.ScoreResult(
                name="KUComplexity",
                value=response_dict["KUComplexity"]["score"],
                reason=response_dict["KUComplexity"]["reason"]
            ),
            score_result.ScoreResult(
                name="KURedundancy",
                value=response_dict["KURedundancy"]["score"],
                reason=response_dict["KURedundancy"]["reason"]
            )
        ]
