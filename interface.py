from retriever import retrieve
from generator import generate


def main():
    print("=" * 60)
    print("  Lehigh University Dining Guide (Unofficial)")
    print("  Powered by student reviews + RAG")
    print("  Type 'quit' to exit")
    print("=" * 60)
    print()

    while True:
        try:
            query = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print("\nSearching sources...")
        chunks = retrieve(query, k=5)

        print("Generating answer...\n")
        answer = generate(query, chunks)

        print("Answer:")
        print("-" * 60)
        print(answer)
        print("-" * 60)

        unique_sources = sorted(set(c["source"] for c in chunks))
        print(f"Sources searched: {', '.join(unique_sources)}")
        print()


if __name__ == "__main__":
    main()
