from typing import List
from dataclasses import dataclass, field

from domain.entities.claim import Claim


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

