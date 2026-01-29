from typing import List, NewType
from dataclasses import dataclass, field

from domain.entities.document import DocumentID
from domain.entities.claim import Claim

KnowledgeUnitID = NewType("KnowledgeUnitID", str)


@dataclass(kw_only=True)
class KnowledgeUnit:
    """A base class for knowledge units (claims or skills)."""
    id: KnowledgeUnitID
    description: str
    importance: float = field(default=0.0)  # 0.0 to 1.0
    mastery_level: float = field(default=0.0)  # 0.0 to 1.0
    document_references: List[DocumentID] = field(default_factory=list)


@dataclass(kw_only=True)
class SkillKnowledge(KnowledgeUnit):
    """Knowledge about a skill derived from one or more claims."""
    source_claims: List[Claim]


@dataclass(kw_only=True)
class FactKnowledge(KnowledgeUnit):
    """Knowledge about a document claim."""
    # source_claims: List[Claim]  #  NOTE: We may have to update this if we want to infer complex claims from simpler ones
    target_claim: Claim

