import re
from typing import List, Dict, Any

class QueryAnalyzer:
    """
    Deconstructs user questions and extracted claims into targeted search queries
    optimized for authoritative external verification.
    """

    @classmethod
    def generate_verification_queries(cls, claim_text: str, category: str = "general") -> List[str]:
        # Strip trailing punctuation
        clean_text = claim_text.strip().rstrip(".")

        queries = [clean_text]

        # Entity-based query optimization
        if category == "location":
            queries.append(f"{clean_text} official location coordinates")
        elif category == "date":
            queries.append(f"{clean_text} historical timeline primary sources")
        elif category == "person":
            queries.append(f"{clean_text} biography official archives")
        elif category == "technical":
            queries.append(f"{clean_text} specification documentation")
        elif category == "statistic":
            queries.append(f"{clean_text} study peer reviewed statistics")

        return queries[:2]
