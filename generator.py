import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_key_here":
            raise ValueError("GROQ_API_KEY not set — copy .env.example to .env and add your key.")
        _client = Groq(api_key=api_key)
    return _client


def generate(query: str, chunks: list) -> str:
    """
    Build a grounded prompt from the retrieved chunks and call Groq to generate an answer.

    Grounded generation means the LLM is explicitly told to answer only from the
    provided sources and to cite them inline. This prevents the model from mixing in
    facts from its training data that aren't in our documents.

    Args:
        query:  the user's question
        chunks: list of dicts from retrieve(), each with 'text' and 'source' keys

    Returns:
        The model's answer as a string, with inline [source] citations.
    """
    # Format each chunk as a numbered source block with its filename visible
    sources_block = ""
    for i, chunk in enumerate(chunks, 1):
        sources_block += f"[{i}] {chunk['source']}\n{chunk['text']}\n\n"

    system_message = (
        "You are an unofficial student guide to dining at Lehigh University, "
        "built from real student reviews, official dining information, and campus resources.\n\n"
        "Rules:\n"
        "- Answer using ONLY the information in the numbered sources provided.\n"
        "- Cite sources inline using the filename in square brackets, e.g. [student_review1.txt].\n"
        "- If a source is particularly relevant, quote it briefly.\n"
        "- If the answer is not present in the sources, say: "
        "'I don't have enough information in my sources to answer that.'\n"
        "- Do not add facts from your own training data."
    )

    user_message = f"Sources:\n{sources_block}\nQuestion: {query}"

    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
