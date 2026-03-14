"""
Attachment processing utilities for file uploads.
Handles validation, PDF text extraction, and image preparation.
"""

import base64
import io
from typing import Tuple

# Magic bytes for supported file types
MAGIC_BYTES = {
    b'\x89PNG\r\n\x1a\n': 'image/png',
    b'\xff\xd8\xff': 'image/jpeg',
    b'GIF87a': 'image/gif',
    b'GIF89a': 'image/gif',
    b'RIFF': 'image/webp',  # WEBP starts with RIFF....WEBP
    b'%PDF': 'application/pdf',
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_PDF_TEXT_CHARS = 30_000


def validate_attachment(data_b64: str, claimed_content_type: str) -> Tuple[bytes, str]:
    """Validate and decode a base64-encoded attachment.

    Returns (decoded_bytes, verified_content_type).
    Raises ValueError on invalid input.
    """
    try:
        raw = base64.b64decode(data_b64)
    except Exception:
        raise ValueError("Invalid base64 encoding")

    if len(raw) > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit")

    if len(raw) < 4:
        raise ValueError("File too small to identify")

    # Verify magic bytes match claimed content type
    detected_type = None
    for magic, mime in MAGIC_BYTES.items():
        if magic == b'RIFF':
            # WEBP: RIFF....WEBP
            if raw[:4] == b'RIFF' and len(raw) > 11 and raw[8:12] == b'WEBP':
                detected_type = 'image/webp'
                break
        elif raw[:len(magic)] == magic:
            detected_type = mime
            break

    if detected_type is None:
        raise ValueError("Unsupported file type. Accepted: PNG, JPEG, GIF, WEBP, PDF")

    if detected_type != claimed_content_type:
        raise ValueError(
            f"File content ({detected_type}) does not match declared type ({claimed_content_type})"
        )

    return raw, detected_type


def extract_pdf_text(raw_bytes: bytes) -> str:
    """Extract text from a PDF using pymupdf. Truncates at MAX_PDF_TEXT_CHARS."""
    import fitz  # pymupdf

    doc = fitz.open(stream=raw_bytes, filetype="pdf")
    pages = []
    total_chars = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        if not text:
            continue

        remaining = MAX_PDF_TEXT_CHARS - total_chars
        if remaining <= 0:
            pages.append(f"\n[... truncated at {MAX_PDF_TEXT_CHARS:,} characters ...]")
            break

        if len(text) > remaining:
            text = text[:remaining]
            pages.append(f"--- Page {page_num + 1} ---\n{text}\n[... truncated ...]")
            break
        else:
            pages.append(f"--- Page {page_num + 1} ---\n{text}")
            total_chars += len(text)

    doc.close()

    if not pages:
        raise ValueError("PDF contains no extractable text")

    return "\n\n".join(pages)
