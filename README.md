# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

I chose Campus dining experiences at my school (Lehigh University). This knowledge is hard to find through official channels because even though Lehigh's dining website tells you hours and locations. It won't tell you specific information such as if a certain station in the main dining hall always has long wait time on weekday mornings, or that students on the unlimited meal plan actually save money eating off-campus on weekends.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Reddit | Student reviews of Food at Lehigh | https://www.reddit.com/r/Lehigh/comments/1k8v2ru/food_for_incoming_freshmen/ |
| 2 | Yelp | Reviews of Rathbone (Main dining hall) Food | https://www.yelp.com/biz/rathbone-bethlehem |
| 3 | Lehigh Sodexo | Lehigh's Official Dinning website | https://lehigh.sodexomyway.com/en-us/locations/ |
| 4 | Brown and White | University Article on Meal plan and dining changes | https://thebrownandwhite.com/2025/09/12/meal-plan-and-dining-changes-cause-mixed-student-reactions/ |
| 5 | Reddit |Addional Student reviews | https://www.reddit.com/r/Lehigh/comments/uwg358/how_is_the_dining_hall_food_at_lehigh/ |
| 6 | Lehigh Offical Blog Website | A student's Favorite Restaurants in Bethlehem, Pa  | https://blog.lehigh.edu/a-foodies-5-favorite-restaurants-in-bethlehem-pa |
| 7 | Lehigh PDF Dietiation Guide | Detailed overview on Dining with Dietary Restrictions | ./documents/dietary_restrictions.txt |
| 8 | Lehigh Sodexo | Meal Plan Options  | https://lehigh.sodexomyway.com/en-us/meal-plan/meal-plan-options|
| 9 | Yelp | Resturant reviews near Lehigh| https://www.yelp.com/search?find_near=lehigh-university-bethlehem&l=g%3A-75.37010279846594%2C40.617429838019575%2C-75.38307364189582%2C40.60568241189106 |
| 10 | Reddit | Student Food reviews | https://www.reddit.com/r/Lehigh/comments/g83s2n/food_at_lehigh/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 150

**Overlap:** 35

**Why these choices fit your documents:** I initially wanted to use 200 characters as my chunk size and 50 for overlap, but this produced fewer than 50 total chunks, so I reduced both for better retrieval . The overlap helps carry semantic context across chunk boundaries so meaning isn't lost at splits. Before chunking, I manually converted webpages and PDFs to plain text files, then cleaned them up by removing unnecessary whitespace.

**Final chunk count:** 55 Chunks

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model Used:** all-MiniLM-L6-v2 via sentence-transformers ( runs fully locally with no API key or cost)

**Production tradeoff reflection:**
With no cost constraint I'd weigh the context length, domain accuracy, multilingual support, and latency. The model I chose (all-MiniLM-L6-v2) caps at 256 tokens, so longer documents get truncated. Thus a different model might support thousands of tokens which would handle richer source material better. Also a students writing may be informal and slang heavy so a model fine-tuned on that would retrieve more precisely. Additionally, a real campus tool likely need to serve non-English speakers, where a multilingual model would be the better fit. Lastly local models return embeddings instantly while cloud API models add network round-trip time on every query, which matters at scale.

---

## Grounded Generation

<!-- Explain how your system enforces grounding - how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

My System Prompt included the following instruction:

- *"Answer using ONLY the information in the provided sources."*
- *"Cite every claim inline with the source filename in square brackets, e.g. [student_review1.txt]."*
- *"Focus on whichever sources best answer the question — ignore sources that are not relevant and do not mention them."*
- *"If one source gives a partial answer and another gives a fuller one, use the fuller one."*
- *"Only say 'I don't have enough information' if NONE of the sources address the question."*
- *"Do not add facts from your own training data."*

Beyond the text instruction, there are two structural choices that reinforce grounding. First, each retrieved chunk is formatted in the prompt as `[filename]\n<chunk text>` — the filename is the header, not a number so the model has no choice but to reference documents by their actual names when it cites. Second, the temperature is set to `0.2`, which keeps the model close to the source text and discourages creative elaboration.

**How source attribution is surfaced in the response:**

The LLM produces inline citations using the exact filename it was given in the source header, for example `[meal_plan_changes.txt]`. This works because the prompt labels every chunk with its filename before the text, so when the model writes a claim, it copies that label into its citation.

In the Gradio UI, a "Sources retrieved" panel shows the unique filenames from all k=5 retrieved chunks. This is built by collecting the `source` field from each chunk and deduplicating with a `set()` — so if three of the five chunks came from the same file, that file appears only once. The panel reflects what was searched, not necessarily what the model cited, since the model is instructed to ignore chunks it finds irrelevant.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How do students describe the quality of food at Lehigh dining halls compared to off-campus alternatives? | On-campus food is decent but overpriced; Rathbone is a hit or miss. Off-campus options like Nawab Indian Restaurant and Hi-Pot are recommended. | Described on-campus dining as "pretty decent but overpriced" and noted the meal plan isn't worth $3k; said it couldn't find a direct comparison to off-campus options | Partially relevant - retrieved meal plan and general review chunks instead of the off-campus restaurant sources | Partially accurate — correctly described on-campus quality but missed the off-campus comparison entirely |
| 2 | What food allergies or dietary accommodations do students say Lehigh dining handles well or poorly? | Students report vegan options are avaliable at Rathbone such as Simple Servings which use ingredients that do not contain milk, eggs, wheat, soy, shellfish, peanuts, tree nuts, sesame, or gluten. | Lehigh offers allergy-friendly options like Simple Servings (and SimpleZone), which avoid common allergens like milk, eggs, gluten, peanuts, and tree nuts. Staff are trained in food allergy safety, and dietitians and dining staff are available to help students with dietary needs, though cross-contact can’t be fully eliminated. A student with celiac disease also said she was able to eat safely at Lehigh but had to be careful when choosing meals. | Relevant | Accurate |
| 3 | How long are the wait times at Hawks Nest for lunch if I order French Fries? | Not uncommon to wait 40 minutes for an order of French fries | "Wait times of 40 minutes for fries are not uncommon at Hawks Nest" | Relevant - exact match to source | Accurate |
| 4 | What changes has Lehigh made to the meal plans and how do students feel about it? | Plans reduced from 8 to 6; meal swipes can no longer be exchanged for dining dollars — replaced with "meal exchanges." Cost increased to $3,690/semester. Students have mixed reactions, with some frustrated by the lost flexibility. | Covered the 8 -> 6 plan reduction, loss of swipe-to-dollar exchange, cost increase to $3,690/semester, and mixed student reactions with quotes | Relevant and even more notable meal_plan_changes.txt dominated the top-k results | Accurate |
| 5 | Where can I find some good local Chinese food around Lehigh? | ShangWei Szechuan in Bethlehem serves authentic Szechuan cuisine including Kung Pao chicken and Dandan noodles. U & Tea dishes like stir-fried string beans and chicken ho fun noodles. | Students can find good local Chinese food at ShangWei Szechuan in Bethlehem, which serves spicy and flavorful Chinese food [blog_post_.txt]. Additionally, U & Tea is another option in the Lehigh Valley that offers well-prepared Chinese dishes, including stir-fried string beans and chicken ho fun noodles [off_campus_food.txt]. |Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Where can I eat off campus?

**What the system returned:** I don't have enough information to provide a comprehensive answer about eating off campus, as the provided sources primarily discuss on-campus dining options [student_review1.txt, student_review3.txt, dietary_restrictions.txt]. None of the sources mention specific off-campus dining locations.

**Root cause (tied to a specific pipeline stage):** The failure is in the retrieval stage. The query "Where can I eat off campus?" is vague and doesn't share vocabulary with how the off-campus content is actually written. Even though `blog_post_.txt` and `off_campus_food.txt` name specific restaurants like ShangWei Szechuan and Hi-Pot, they never ever using the phrase "off campus." Meanwhile, the on-campus review chunks do use the phrase "off campus" as a comparison point ("the dining hall isn't worth it, just eat off campus"), so those ranked higher in cosine similarity.

**What you would change to fix it:** Add a query expansion step before retrieval and generate two or three semantically related queries (e.g., "restaurants near Lehigh," "Bethlehem dining options," "places to eat in Bethlehem PA") and merge the top-k results from each before passing to the generator. This would surface the off-campus restaurant chunks even when the original query doesn't share their vocabulary.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

The evaluation plan's 5 test questions with expected answers gave me concrete targets to test against while building. Instead of guessing whether retrieval was working, I could run Q3 ("How long are the wait times at Hawks Nest for French fries?") and check whether the 40-minute answer came back from the right source. When it did, I knew chunk size and cosine similarity were calibrated correctly. Without those pre-written expected answers I would have had no clear way to tell good retrieval from lucky retrieval.

**One way your implementation diverged from the spec, and why:**

The spec planned for 200–250 word chunks with 50-word overlap, but after ingesting all documents I ended up with fewer than 50 total chunks at that size which was too few to give the retriever meaningful choices. I reduced chunk size to 150 words and overlap to 35, which brought the total to 55 chunks. The spec was written before I knew how short the source documents would actually be after converting to txt documents and cleaning whitespace, so the numbers that made sense on paper needed adjusting once I saw the real data.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* The Chunking Strategy section from planning.md (chunk_size ~200–250 words, overlap ~50 words, sentence boundaries) and asked Claude to implement `chunk_text()`.
- *What it produced:* A function that split on a fixed character count every 200 characters, with no awareness of sentence boundaries.
- *What I changed or overrode:* Rewrote the split logic to first break on paragraphs, then on sentence-ending punctuation (`(?<=[.!?])\s+`), and accumulate whole sentences into chunks rather than cutting at a character position. I also reduced the target from 200 words to 150 after seeing the character-based approach was leaving mid-sentence cuts throughout the chunks.

**Instance 2**

- *What I gave the AI:* The Grounded Generation requirement and a description of how I wanted inline source attribution to work, and asked Claude to write the system prompt for `generator.py`.
- *What it produced:* A system prompt that told the model to cite sources as numbered references — [1], [2], [3] — matching the order chunks appeared in the prompt.
- *What I changed or overrode:* Changed the citation format from numbered references to actual filenames (e.g., `[meal_plan_changes.txt]`). Numbered citations break as soon as retrieval returns chunks in a different order on the next query — the model would cite [2] but [2] now points to a different document. Filenames are stable regardless of retrieval order, so attribution stays correct.
