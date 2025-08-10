"""
Evaluation utilities for abstract quality.
"""

def evaluate_abstract(abstract: str) -> dict:
    """
    Example heuristic evaluation: checks length and keyword presence.
    """
    word_count = len(abstract.split())
    keywords = ["research", "method", "result", "conclusion"]
    score = sum(1 for kw in keywords if kw in abstract.lower())

    return {
        "word_count": word_count,
        "keyword_match_score": score,
        "keywords_present": [kw for kw in keywords if kw in abstract.lower()]
    }