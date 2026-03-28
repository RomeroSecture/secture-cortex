"""Text chunking service for RAG pipeline.

Splits text into chunks of ~512 tokens with 50 token overlap.
Uses a simple word-based approximation (1 token ≈ 0.75 words).
"""

CHUNK_SIZE_TOKENS = 512
OVERLAP_TOKENS = 50
# Approximate: 1 token ≈ 0.75 words → 512 tokens ≈ 384 words
CHUNK_SIZE_WORDS = int(CHUNK_SIZE_TOKENS * 0.75)
OVERLAP_WORDS = int(OVERLAP_TOKENS * 0.75)


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks of approximately 512 tokens.

    Returns a list of text chunks. Empty input returns an empty list.
    """
    if not text or not text.strip():
        return []

    words = text.split()
    if len(words) <= CHUNK_SIZE_WORDS:
        return [text.strip()]

    chunks: list[str] = []
    start = 0

    while start < len(words):
        end = start + CHUNK_SIZE_WORDS
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - OVERLAP_WORDS

    return chunks
