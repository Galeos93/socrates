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
        return """Adapt the questions for LOW mastery:
        - Use straightforward, direct questions
        - Focus on basic recall and understanding
        - Avoid complex scenarios or edge cases
        - Set difficulty_level: 1-2"""
    elif mastery_level < 0.6:
        return """Adapt the questions for MODERATE mastery:
        - Use questions that require some analysis
        - Include practical application scenarios
        - Test deeper understanding
        - Set difficulty_level: 2-4"""
    else:
        return """Adapt the questions for HIGH mastery:
        - Use challenging, nuanced questions
        - Include complex scenarios or edge cases
        - Test advanced application and critical thinking
        - Require synthesis of multiple concepts
        - Set difficulty_level: 4-5"""


def build_batch_question_creation_prompt(ku: KnowledgeUnit, count: int) -> str:
    """
    Builds a prompt for generating up to `count` non-redundant questions
    from a KnowledgeUnit. The model is explicitly instructed to generate
    fewer questions when additional ones would be redundant.
    """

    if isinstance(ku, FactKnowledge):
        source_texts = ku.target_claim.text
        mastery_guidance = _get_mastery_guidance(ku.mastery_level)

        prompt = f"""
        You are generating assessment questions for a learner.

        Your task is to generate UP TO {count} questions to test understanding of the following fact.
        {count} is a MAXIMUM, not a requirement.

        Fact Description:
        {ku.description}

        Source Claim (for your reference only):
        {source_texts}

        Current Mastery Level:
        {ku.mastery_level:.2f} (0.0 = beginner, 1.0 = expert)

        {mastery_guidance}

        QUESTION GENERATION RULES (STRICT):

        - Generate ONLY as many questions as can be meaningfully distinct.
        - If the fact is simple and supports only a small number of unique questions, generate fewer questions.
        - Do NOT force the question count.
        - STOP generating questions once all distinct ways of testing this fact have been exhausted.

        DIVERSITY REQUIREMENT:

        - Each question must test a genuinely different aspect, perspective, or formulation of the fact.
        - Differences in wording alone do NOT count as diversity.
        - Do NOT produce paraphrases that test the same understanding in the same way.

        CONTENT RULES:

        - Each question must be self-contained and answerable WITHOUT access to the source claim.
        - Do NOT reference the source claim, document, or text in any way.
        - The learner will ONLY see the question.

        OUTPUT FORMAT (JSON ONLY):

        Return a JSON object with the following structure.
        Do not enclose it with ````json` markdown.
        The "questions" array MUST contain ≤ {count} items.

        {{
            "questions": [
                {{
                    "question_text": "string",
                    "answer": "string",
                    "difficulty_level": 1-5
                }}
            ]
        }}
        """

    elif isinstance(ku, SkillKnowledge):
        claims_texts = " ; ".join(c.text for c in ku.source_claims)
        mastery_guidance = _get_mastery_guidance(ku.mastery_level)

        prompt = f"""
        You are generating assessment questions for a learner.

        Your task is to generate UP TO {count} applied questions to test the following skill.
        {count} is a MAXIMUM, not a requirement.

        Skill Description:
        {ku.description}

        Source Claims (for your reference only):
        {claims_texts}

        Current Mastery Level:
        {ku.mastery_level:.2f} (0.0 = beginner, 1.0 = expert)

        {mastery_guidance}

        QUESTION GENERATION RULES (STRICT):

        - Generate ONLY as many questions as can be meaningfully distinct.
        - If the skill supports only a limited number of realistic or unique scenarios, generate fewer questions.
        - Do NOT force the question count.
        - STOP generating questions once all distinct application scenarios have been covered.

        DIVERSITY REQUIREMENT:

        - Each question must present a genuinely different application context.
        - Superficial changes that do not alter the skill being tested do NOT count as diversity.
        - Do NOT create multiple questions that test the same procedural step in the same way.

        CONTENT RULES:

        - Each question must be self-contained and answerable WITHOUT access to the source claims.
        - Do NOT reference the source claims, document, or text in any way.
        - The learner will ONLY see the question.

        OUTPUT FORMAT (JSON ONLY):

        Return a JSON object with the following structure.
        Do not enclose it with ````json` markdown.
        The "questions" array MUST contain ≤ {count} items.

        {{
            "questions": [
                {{
                    "question_text": "string",
                    "answer": "string",
                    "difficulty_level": 1-5
                }}
            ]
        }}
        """

    else:
        raise ValueError(f"Unknown KnowledgeUnit type: {type(ku)}")

    return prompt