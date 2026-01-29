
TEMPLATE_V1 = """
    You are an expert at reading a text and breaking it down into discrete, verifiable claims and knowledge units.

    You will extract three types of information:

    1. Claims: Atomic statements from the text that can be verified or inferred. Assign each a unique integer ID.
    2. Facts: Declarative knowledge units based on exactly one claim (target claim).
    3. Skills: Applied/procedural knowledge units based on one or more claims.

    Your output must be strictly JSON in the following format, DO NOT enclose it with
    ``json`` or any other markdown:

    {
    "claims": [
        {"id": 1, "text": "..."},
        {"id": 2, "text": "..."}
    ],
    "facts": [
        {"description": "...", "target_claim_id": 1},
        {"description": "...", "target_claim_id": 2}
    ],
    "skills": [
        {"description": "...", "source_claim_ids": [1,2]},
        {"description": "...", "source_claim_ids": [3]}
    ]
    }

    ---

    Example:

    TEXT:
    "To bake a sourdough loaf, you must first feed your starter to ensure it is active.
    Fermentation occurs because wild yeast consumes sugars and releases carbon dioxide.
    Once the dough has risen, bake it at 450°F. High heat gives the bread its airy structure."

    OUTPUT:

    {
    "claims": [
        {"id": 1, "text": "The sourdough starter must be fed before baking to ensure it is active."},
        {"id": 2, "text": "Fermentation occurs when wild yeast consumes sugars and releases carbon dioxide."},
        {"id": 3, "text": "Dough rises as a result of fermentation."},
        {"id": 4, "text": "Bake the dough at 450°F after it has risen."},
        {"id": 5, "text": "High baking heat is essential for proper oven spring."},
        {"id": 6, "text": "Oven spring gives bread its airy structure."}
    ],
    "facts": [
        {"description": "Feeding the starter ensures it is active and ready for baking.", "target_claim_id": 1},
        {"description": "Fermentation causes the dough to rise.", "target_claim_id": 3},
        {"description": "Baking at high temperature produces proper oven spring and airy bread.", "target_claim_id": 5}
    ],
    "skills": [
        {"description": "Prepare an active sourdough starter before baking.", "source_claim_ids": [1,2]},
        {"description": "Manage fermentation to ensure dough rises properly.", "source_claim_ids": [2,3]},
        {"description": "Bake sourdough at high temperature to achieve proper oven spring.", "source_claim_ids": [4,5,6]}
    ]
    }

    ---

    Now generate Claims, Facts, and Skills for the following text.
    Return **only JSON**, do not include explanations:

    TEXT:
    "{{document_text}}"
    """