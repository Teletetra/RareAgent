ACTIONS = {
    "A1": "Propose one concise reasoning step that advances the answer using the current context.",
    "A2": "Propose the remaining reasoning steps for a straightforward question.",
    "A3": "Decompose the question into a small sequence of answerable sub-questions.",
    "A4": "Re-answer the current sub-question using the strongest available evidence.",
    "A5": "Rephrase the question to make ambiguous conditions explicit.",
    "A6": "Generate targeted search queries from the original question, retrieve evidence, and answer using that evidence.",
    "A7": "Retrieve evidence for the generated sub-question, then revise the sub-answer using the retrieved context.",
}

SYSTEM_PROMPT = """You are a retrieval-augmented reasoning agent. Prefer evidence-grounded answers. Do not invent facts that are absent from the supplied evidence. Return concise reasoning summaries rather than hidden chain-of-thought."""
