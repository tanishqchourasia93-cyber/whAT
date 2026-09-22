from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from documents.parser import DocumentParser
from documents.chunker import DocumentChunker

router = APIRouter(prefix="/api/documents", tags=["documents"])

class DocumentVerificationResult(BaseModel):
    filename: str
    document_length_chars: int
    chunks_created: int
    question: str
    relevant_passages: List[Dict[str, Any]]
    verification_status: str
    explanation: str

@router.post("/verify")
async def verify_against_document(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    try:
        content_bytes = await file.read()
        extracted_text = DocumentParser.parse_bytes(content_bytes, file.filename or "document.txt")
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Document text could not be extracted or is empty.")

        chunks = DocumentChunker.chunk_document(extracted_text)
        relevant = DocumentChunker.find_relevant_passages(question, chunks, top_k=3)

        if not relevant:
            status = "NOT_FOUND"
            explanation = "No relevant sections in the uploaded document discuss this specific claim or topic."
        else:
            best_score = relevant[0]["score"]
            if best_score >= 0.5:
                status = "SUPPORTED"
                explanation = f"Corroborating passage found in section with relevance score {best_score}."
            elif best_score >= 0.2:
                status = "PARTIALLY_SUPPORTED"
                explanation = f"Partial match identified in document text with relevance score {best_score}."
            else:
                status = "UNCERTAIN"
                explanation = "Document mentions peripheral terms, but the evidence is inconclusive."

        return DocumentVerificationResult(
            filename=file.filename or "uploaded_file",
            document_length_chars=len(extracted_text),
            chunks_created=len(chunks),
            question=question,
            relevant_passages=relevant,
            verification_status=status,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document verification error: {str(e)}")
