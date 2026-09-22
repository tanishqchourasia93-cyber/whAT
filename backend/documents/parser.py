import io
from typing import Optional
from pypdf import PdfReader

class DocumentParser:
    """
    Parses uploaded PDF, Markdown, and TXT files for document-grounded verification.
    """

    @classmethod
    def parse_bytes(cls, content_bytes: bytes, filename: str) -> str:
        filename_lower = filename.lower()
        if filename_lower.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(content_bytes))
            text_pages = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    text_pages.append(text.strip())
            return "\n\n".join(text_pages)
        else:
            # Assume text/markdown/txt
            return content_bytes.decode("utf-8", errors="ignore")
