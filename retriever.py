import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "lehigh_dining"
DB_PATH = "./chroma_db"

# Module-level singletons — loading the model takes ~2s, so we do it once per process
_model = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        print("Loading embedding model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=DB_PATH)
        # hnsw:space=cosine means ChromaDB measures similarity by angle between vectors,
        # not raw distance — better for text where direction matters more than magnitude
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def embed_and_store(chunks: list, metadata: list) -> None:
    """
    Encode each chunk with all-MiniLM-L6-v2 and upsert into ChromaDB.

    Args:
        chunks:   list of chunk strings (the text to store)
        metadata: parallel list of dicts, each with 'source' and 'chunk_index'

    Each chunk gets a unique ID of the form 'filename_N' so re-running this
    function updates existing entries rather than creating duplicates (upsert).
    """
    model = _get_model()
    collection = _get_collection()

    print(f"Encoding {len(chunks)} chunks...")
    # normalize_embeddings=True makes every vector a unit vector, which is required
    # for cosine similarity to work correctly (dot product = cosine similarity)
    embeddings = model.encode(chunks, show_progress_bar=True, normalize_embeddings=True)

    ids = [f"{m['source']}_{m['chunk_index']}" for m in metadata]

    collection.upsert(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=metadata,
    )
    print(f"Stored {collection.count()} chunks in ChromaDB collection '{COLLECTION_NAME}'.")


def retrieve(query: str, k: int = 5) -> list:
    """
    Embed the query and return the top-k most semantically similar chunks.

    Returns a list of dicts, each with:
        text        — the raw chunk text
        source      — filename the chunk came from
        chunk_index — position of this chunk within its source file
        similarity  — cosine similarity score in [0, 1] (higher = more relevant)
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            # ChromaDB cosine distance = 1 - cosine_similarity, so we invert it
            "similarity": round(1 - dist, 4),
        })

    return chunks


if __name__ == "__main__":
    from ingest import load_and_chunk_all

    # --- Step 1: Load, chunk, and store all documents ---
    print("=== Step 1: Ingesting documents ===")
    all_chunks = load_and_chunk_all()
    texts = [c["text"] for c in all_chunks]
    metadata = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in all_chunks]
    embed_and_store(texts, metadata)

    # --- Step 2: Verify retrieval with a known query (from planning.md) ---
    print("\n=== Step 2: Retrieval verification ===")
    test_query = "What are the dining options on campus?"
    print(f"Query: '{test_query}'")
    print("-" * 60)

    results = retrieve(test_query, k=4)
    for i, r in enumerate(results, 1):
        score = r["similarity"]
        flag = " <-- TARGET" if score >= 0.7 else ""
        print(f"\n[{i}] {r['source']}  |  similarity: {score}{flag}")
        print(r["text"][:300])
