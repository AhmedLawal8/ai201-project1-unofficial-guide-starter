import os
import re


def clean_text(raw: str) -> str:
    """Strip trailing whitespace per line and collapse excess blank lines."""
    lines = [line.rstrip() for line in raw.splitlines()]
    # Collapse 3+ consecutive blank lines into just 2, to preserve some visual separation
    cleaned = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines))
    return cleaned.strip()


def chunk_text(text: str, chunk_size: int = 150, overlap: int = 35) -> list:
    """
    Split text into overlapping chunks that respect sentence boundaries.

    Strategy (from planning.md):
      - chunk_size: target max words per chunk (~150 words ≈ 195 tokens, well within
        the 256-token limit of all-MiniLM-L6-v2)
      - overlap: words carried from the end of one chunk into the start of the next,
        so a sentence that straddles a boundary isn't lost
      - Boundaries: split on paragraphs first, then on sentence-ending punctuation,
        so we never cut mid-sentence
    """
    # Step 1: split into paragraphs, then into sentences within each paragraph
    paragraphs = re.split(r'\n\n+', text)
    sentences = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Split on sentence-ending punctuation followed by whitespace
        para_sentences = re.split(r'(?<=[.!?])\s+', para)
        sentences.extend(s.strip() for s in para_sentences if s.strip())

    # Step 2: accumulate sentences into chunks, rolling overlap on each boundary
    chunks = []
    current_words = []

    for sentence in sentences:
        sentence_words = sentence.split()
        if current_words and len(current_words) + len(sentence_words) > chunk_size:
            chunks.append(' '.join(current_words))
            # Seed the next chunk with the tail of the current one (the overlap)
            current_words = current_words[-overlap:] + sentence_words
        else:
            current_words.extend(sentence_words)

    # Add any remaining words as the final chunk
    if current_words:
        chunks.append(' '.join(current_words))

    return chunks


def load_and_chunk_all(docs_dir: str = "documents") -> list:
    """Read every .txt file in docs_dir, clean it, chunk it, and return all chunks
    with metadata needed for the vector store in Milestone 4."""
    results = []
    for filename in sorted(os.listdir(docs_dir)):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(docs_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
        text = clean_text(raw)
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            results.append({
                "text": chunk,
                "source": filename,
                "chunk_index": i,
            })
    return results


if __name__ == "__main__":
    all_chunks = load_and_chunk_all()
    print(f"Total chunks produced: {len(all_chunks)}\n")

    # Print the first chunk from each source so you can visually verify
    # that chunks are readable and not cut mid-sentence
    for chunk_data in all_chunks:
        src = chunk_data["source"]
        id = chunk_data["chunk_index"]
        words = len(chunk_data["text"].split())
        print(f"=== {src}_{id}  (chunk  - {words} words) ===")
        print(chunk_data["text"])
        print()
