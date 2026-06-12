import gradio as gr
from retriever import retrieve
from generator import generate

# The 5 evaluation questions from planning.md — pre-loaded as clickable examples
EXAMPLES = [
    "How do students describe the quality of food at Lehigh dining halls compared to off-campus alternatives?",
    "What food allergies or dietary accommodations does Lehigh dining handle well or poorly?",
    "How long are the wait times at Hawks Nest for lunch if I order French Fries?",
    "What changes has Lehigh made to the meal plans and how do students feel about it?",
    "Where can I find some good local Chinese food around Lehigh?",
]


def answer_question(question: str):
    if not question.strip():
        return "Please enter a question.", ""

    chunks = retrieve(question, k=5)
    answer = generate(question, chunks)
    
    unique_sources = sorted(set(c["source"] for c in chunks))
    sources_text = "\n".join(f"• {s}" for s in unique_sources)

    return answer, sources_text


with gr.Blocks(title="Lehigh Dining Guide") as demo:
    gr.Markdown(
        "# Lehigh University Dining Guide (Unofficial)\n"
        "Ask anything about on-campus dining, meal plans, dietary restrictions, or nearby restaurants. "
        "Answers are grounded in real student reviews and official Lehigh dining sources."
    )

    question_input = gr.Textbox(
        label="Your question",
        placeholder="e.g. How long are wait times at Hawks Nest for lunch?",
        lines=2,
    )

    gr.Examples(examples=EXAMPLES, inputs=question_input, label="Try one of your evaluation questions")

    submit_btn = gr.Button("Ask", variant="primary")

    answer_output = gr.Markdown(label="Answer")
    sources_output = gr.Textbox(label="Sources retrieved", interactive=False, lines=4)

    # Both the button click and pressing Enter in the textbox trigger the same function
    submit_btn.click(fn=answer_question, inputs=question_input, outputs=[answer_output, sources_output])
    question_input.submit(fn=answer_question, inputs=question_input, outputs=[answer_output, sources_output])


if __name__ == "__main__":
    demo.launch()
