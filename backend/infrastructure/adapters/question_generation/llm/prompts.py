from domain.entities.knowledge_unit import FactKnowledge, SkillKnowledge, KnowledgeUnit        


def build_question_creation_prompt(ku: KnowledgeUnit) -> str:
    """Builds a prompt for extracting a question from a KnowledgeUnit.

    Parameters
    ----------
    ku: KnowledgeUnit
        The fact or skill to generate a question for.

    Returns
    -------
    str
        The constructed prompt.
    """
    if isinstance(ku, FactKnowledge):
        source_texts = ku.target_claim.text
        prompt = f"""
        Generate a concise question to test comprehension of the following fact:

        Fact: {ku.description}
        Source Claim: {source_texts}

        Output JSON format only, DO NOT enclose it with
        ``json`` or any other markdown:
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

        Output JSON format only, DO NOT enclose it with
        ``json`` or any other markdown:
        {{
            "question_text": "string",
            "answer": "string",
            "difficulty_level": 1-5
        }}
        """
    else:
        raise ValueError(f"Unknown KnowledgeUnit type: {type(ku)}")

    return prompt