import re
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from providers.base import LLMResponse, LLMProvider

class FactualClaim(BaseModel):
    id: str
    original_text: str
    normalized_claim: str
    source_model: str
    importance: str = "high"  # "high" | "medium" | "low"
    category: str = "general" # "location" | "date" | "person" | "statistic" | "technical" | "general"
    verification_status: str = "PENDING"  # "SUPPORTED" | "CONTRADICTED" | "UNCERTAIN" | "NOT_VERIFIABLE"
    models_supporting: List[str] = Field(default_factory=list)
    models_contradicting: List[str] = Field(default_factory=list)
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    contradicting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: Optional[str] = None
    confidence_level: str = "UNVERIFIED" # "HIGH CONFIDENCE" | "MEDIUM CONFIDENCE" | "LOW CONFIDENCE" | "UNVERIFIED"

class ClaimExtractor:
    """
    Extracts atomic, verifiable factual claims from multi-LLM outputs.
    Deconstructs compound sentences into atomic propositions.
    """

    @classmethod
    async def extract_claims(
        cls,
        responses: List[LLMResponse],
        llm_provider: Optional[LLMProvider] = None
    ) -> List[FactualClaim]:
        all_claims: List[FactualClaim] = []
        claim_counter = 1

        for resp in responses:
            if resp.status != "success" or not resp.content.strip():
                continue

            extracted = await cls._extract_from_text(
                text=resp.content,
                model_name=resp.provider_name,
                start_id=claim_counter,
                llm_provider=llm_provider
            )
            all_claims.extend(extracted)
            claim_counter += len(extracted)

        return all_claims

    @classmethod
    async def _extract_from_text(
        cls,
        text: str,
        model_name: str,
        start_id: int,
        llm_provider: Optional[LLMProvider] = None
    ) -> List[FactualClaim]:
        # Try LLM structured extraction if a configured provider is passed
        if llm_provider and llm_provider.is_configured():
            try:
                extraction_prompt = f"""
You are an expert fact-checking claim extraction engine.
Analyze the following text and extract discrete, atomic factual claims.
Each claim MUST be an independent, self-contained statement that can be verified as TRUE or FALSE with empirical evidence.
DO NOT include purely subjective opinions or meta-statements.

Text:
\"\"\"
{text}
\"\"\"

Return ONLY a JSON list of objects with the schema:
[
  {{
    "normalized_claim": "The exact atomic factual statement",
    "original_sentence": "The sentence it came from",
    "category": "date" | "location" | "person" | "statistic" | "technical" | "general",
    "importance": "high" | "medium" | "low"
  }}
]
"""
                res = await llm_provider.generate(extraction_prompt)
                if res.status == "success" and res.content:
                    # Clean markdown fence if present
                    clean_json = res.content.strip()
                    if clean_json.startswith("```"):
                        clean_json = re.sub(r"^```[a-zA-Z]*\n?", "", clean_json)
                        clean_json = re.sub(r"\n?```$", "", clean_json)
                    items = json.loads(clean_json)
                    claims = []
                    for idx, item in enumerate(items):
                        claims.append(
                            FactualClaim(
                                id=f"claim_{start_id + idx}",
                                original_text=item.get("original_sentence", item.get("normalized_claim")),
                                normalized_claim=item.get("normalized_claim"),
                                source_model=model_name,
                                importance=item.get("importance", "high"),
                                category=item.get("category", "general"),
                                models_supporting=[model_name]
                            )
                        )
                    if claims:
                        return claims
            except Exception:
                pass  # Fall back to linguistic decomposition

        # Linguistic / Heuristic Decomposition Fallback
        return cls._heuristic_extraction(text, model_name, start_id)

    @classmethod
    def _heuristic_extraction(cls, text: str, model_name: str, start_id: int) -> List[FactualClaim]:
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        claims = []
        c_id = start_id

        for sentence in sentences:
            sentence = sentence.strip().strip('"').strip("'")
            if len(sentence) < 15:
                continue

            # Check if sentence contains compound clauses with "and", "by", "in"
            # Sub-split into atomic claims
            sub_clauses = cls._split_into_atomic_propositions(sentence)
            for clause in sub_clauses:
                if len(clause) < 10:
                    continue
                category = cls._infer_category(clause)
                claims.append(
                    FactualClaim(
                        id=f"claim_{c_id}",
                        original_text=sentence,
                        normalized_claim=clause,
                        source_model=model_name,
                        importance="high" if any(char.isdigit() for char in clause) or category in ["location", "person", "date"] else "medium",
                        category=category,
                        models_supporting=[model_name]
                    )
                )
                c_id += 1

        return claims

    @classmethod
    def _split_into_atomic_propositions(cls, sentence: str) -> List[str]:
        # Target compound statements:
        # e.g. "The Taj Mahal was built in 1648 by Shah Jahan. It is located in Delhi and was designed by Ustad Ahmad Lahori."
        clauses = []
        
        # Simple splitting on conjunctions when clauses have subjects/verbs
        parts = re.split(r',\s*(?:and|while|although|with)\s+|\s+and\s+(?:was|is|it\s+is|it\s+was)\s+', sentence, flags=re.IGNORECASE)
        for part in parts:
            p = part.strip().rstrip(".;,")
            if p:
                if not p.endswith("."):
                    p += "."
                clauses.append(p)
        return clauses if clauses else [sentence]

    @classmethod
    def _infer_category(cls, text: str) -> str:
        text_lower = text.lower()
        if re.search(r'\b(1[5-9]\d\d|20\d\d|january|february|march|april|may|june|july|august|september|october|november|december)\b', text_lower):
            return "date"
        if re.search(r'\b(located in|situated in|capital|city|country|delhi|agra|india|california|beijing)\b', text_lower):
            return "location"
        if re.search(r'\b(shah jahan|jobs|steve jobs|ustad ahmad lahori|built by|designed by|founded by|commissioned by)\b', text_lower):
            return "person"
        if re.search(r'\b(\d+([.,]\d+)?%|\d+\s*(deaths|fatalities|twh|billion|million))\b', text_lower):
            return "statistic"
        if re.search(r'\b(isa|risc-v|arm|processor|instruction set|architecture|compiler|gsm)\b', text_lower):
            return "technical"
        return "general"
