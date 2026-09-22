import re
from typing import List, Dict, Any

class DocumentChunker:
    """
    Chunks long documents into overlapping segments and retrieves relevant passages
    for document-grounded claim verification.
    """

    @classmethod
    def chunk_document(cls, text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += (chunk_size - overlap)
            if start >= len(words) - overlap:
                break
        return chunks if chunks else [text]

    @classmethod
    def find_relevant_passages(cls, query: str, chunks: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
        if not query_words:
            return []

        scored_chunks = []
        for idx, chunk in enumerate(chunks):
            chunk_words = set(re.findall(r'\b\w{3,}\b', chunk.lower()))
            overlap = len(query_words & chunk_words)
            if overlap > 0:
                score = overlap / len(query_words)
                scored_chunks.append({
                    "passage_id": f"chunk_{idx+1}",
                    "passage": chunk[:400] + ("..." if len(chunk) > 400 else ""),
                    "score": round(score, 3)
                })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]
