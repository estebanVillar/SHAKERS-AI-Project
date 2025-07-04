# Recommendation System Part 2: The Recommendation Generation Logic

## 1. Goal: Proactive and Relevant Suggestions

Once a user profile with an interest vector exists, the system can generate recommendations. The goal is not merely to suggest popular documents, but to proactively offer 2-3 articles that are highly relevant to the user's current train of thought but that they have not yet consulted. This entire process is handled by the `/api/recommendations` endpoint.

---

## 2. Critical Optimization: The `doc_embeddings_cache`

A naive approach to recommendations would be to re-read and re-embed all documents in the knowledge base every time a recommendation is requested. This would be incredibly slow and costly.

*   **The Chosen Solution:** This project implements a crucial startup optimization. When the Flask server in `main.py` first launches, it iterates through every document in the knowledge base, embeds the *entire page content* of each, and stores this embedding in a Python dictionary called `doc_embeddings_cache`. This dictionary maps the document's `topic` to its content and its pre-computed embedding.

*   **The Benefit:** This one-time, upfront computation means that when a recommendation request comes in, the system has instant access to the vector representation of every document. The recommendation process becomes a series of fast in-memory lookups and calculations, ensuring the API endpoint responds in milliseconds.

---

## 3. The Recommendation Algorithm

The algorithm, found in the `handle_recommendations` function, is a clear, step-by-step process.

1.  **Fetch the User's Profile:** The system retrieves the user's `profile_vector` and their list of `inferred_interests` (topics they've already seen).

2.  **Calculate Similarity Scores:** It then iterates through every single document in the pre-computed `doc_embeddings_cache`. For each document, it calculates the **cosine similarity** between the user's `profile_vector` and the document's embedding.

    *   **What is Cosine Similarity?** It is a metric that measures the cosine of the angle between two vectors. A score of 1 means the vectors point in the exact same direction (perfect similarity of topic), 0 means they are unrelated, and -1 means they are opposites. This is the standard method for comparing thematic relevance in vector space.

3.  **Rank and Sort:** All documents are then sorted in descending order based on their similarity score, placing the most relevant documents at the top of the list.

---

## 4. Intelligent Filtering and Explainability

This is where the system goes beyond a simple "top 3" list to provide a superior user experience, fulfilling the case study requirements for **explainability** and **diversity**.

The system iterates through the ranked list of documents and applies a set of rules to select the final recommendations:

*   **Rule 1: Prioritize New Content:** The algorithm heavily prioritizes documents whose topics are **not** in the user's `inferred_interests` list.

*   **Rule 2: Dynamic Explanations:** Instead of a generic message, the explanation for *why* a document is recommended is generated based on its similarity score and whether the user has seen it before. The logic in the code explicitly checks thresholds:
    *   **Score > 0.45 & Not Seen:** `"Highly relevant to your interests and you haven't seen it yet."` (Strong, direct recommendation)
    *   **Score > 0.45 & Seen:** `"You've touched on this; a review might offer deeper insights."` (Encourages a deeper look)
    *   **Score > 0.35 & Not Seen:** `"To broaden your knowledge, you might find this interesting."` (Suggests a related but potentially new area)

*   **Rule 3: Fill Remaining Slots:** If the above rules don't produce 3 recommendations (for example, if the user is new or has already seen most relevant content), the system will backfill the remaining slots with the next highest-scoring unseen items, ensuring there are always suggestions to explore.

This rule-based approach makes the recommendations feel reasoned and transparent, directly fulfilling the core project requirements.