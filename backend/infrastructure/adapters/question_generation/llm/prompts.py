from domain.entities.knowledge_unit import FactKnowledge, SkillKnowledge, KnowledgeUnit        


def _get_mastery_guidance(mastery_level: float) -> str:
    """Generate guidance for question difficulty based on mastery level.
    
    Parameters
    ----------
    mastery_level: float
        Current mastery level (0.0 to 1.0)
        
    Returns
    -------
    str
        Guidance text for the LLM
    """
    if mastery_level < 0.3:
        return """Adapt the question for LOW mastery:
        - Use straightforward, direct questions
        - Focus on basic recall and understanding
        - Avoid complex scenarios or edge cases
        - Set difficulty_level: 1-2"""
    elif mastery_level < 0.6:
        return """Adapt the question for MODERATE mastery:
        - Use questions that require some analysis
        - Include practical application scenarios
        - Test deeper understanding
        - Set difficulty_level: 2-4"""
    else:
        return """Adapt the question for HIGH mastery:
        - Use challenging, nuanced questions
        - Include complex scenarios or edge cases
        - Test advanced application and critical thinking
        - Require synthesis of multiple concepts
        - Set difficulty_level: 4-5"""


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
        mastery_guidance = _get_mastery_guidance(ku.mastery_level)
        prompt = f"""
        Generate a concise question to test comprehension of the following fact:

        Fact: {ku.description}
        Source Claim: {source_texts}
        Current Mastery Level: {ku.mastery_level:.2f} (0.0 = beginner, 1.0 = expert)

        {mastery_guidance}

        IMPORTANT: The question must be self-contained and answerable WITHOUT seeing the source claim or document.
        Do NOT use phrases like "according to the source claim", "based on the text", "in the document", etc.
        The learner will ONLY see the question, not the source material.

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
        mastery_guidance = _get_mastery_guidance(ku.mastery_level)
        prompt = f"""
        Generate a concise applied question to test the following skill:

        Skill: {ku.description}
        Source Claims: {claims_texts}
        Current Mastery Level: {ku.mastery_level:.2f} (0.0 = beginner, 1.0 = expert)

        {mastery_guidance}

        IMPORTANT: The question must be self-contained and answerable WITHOUT seeing the source claims or document.
        Do NOT use phrases like "according to the source", "based on the text", "in the document", etc.
        The learner will ONLY see the question, not the source material.

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