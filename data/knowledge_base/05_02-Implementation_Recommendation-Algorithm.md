# Implementation: The Recommendation Algorithm

## 1. Overview
Once a user profile with an interest vector exists, the system can generate recommendations. The goal is not merely to suggest popular documents, but to proactively offer 2-3 articles that are highly relevant to the user's current train of thought but that they have not yet consulted. This entire process is handled by the `/api/recommendations` endpoint and its corresponding `handle_recommendations` function in `main.py`.

---

## 2. A Critical Optimization: The `doc_embeddings_cache`
A naive approach to recommendations would be to re-read and re-embed all documents in the knowledge base every single time a recommendation is requested. This would be incredibly slow and costly.

To solve this, our project implements a crucial startup optimization. When the Flask server in `main.py` first launches, it performs a one-time process:
1.  It iterates through every document in the knowledge base.
2.  It embeds the **entire page content** of each one.
3.  It stores this embedding in a Python dictionary called `doc_embeddings_cache`. This dictionary maps each document's `topic` (its unique filename-based identifier) to its full content and its pre-computed embedding.

**The Benefit:** This one-time, upfront computation means that when a recommendation request comes in, the system has instant, in-memory access to the vector representation of every document. The recommendation process becomes a series of lightning-fast lookups and calculations, ensuring the API endpoint responds in milliseconds.

---

## 3. The Recommendation Algorithm: Step-by-Step

### 3.1. Step 1: Fetch the User's Profile
The system first retrieves the specific user's `profile_vector` and their list of `inferred_interests` (topics they've already seen, based on RAG sources) from the `user_profiles.json` file.

### 3.2. Step 2: Calculate Similarity Scores
The algorithm then iterates through every single document in the pre-computed `doc_embeddings_cache`. For each document, it calculates the **cosine similarity** between the user's `profile_vector` and that document's embedding. This gives us a numerical score of thematic relevance for every document in the knowledge base relative to the user's interests.

*For more on this metric, see **`02_03-Concepts-Vector-Embeddings.md`***.

### 3.3. Step 3: Rank and Sort
All documents are then placed in a list and sorted in descending order based on their similarity score, creating a ranked list from most to least relevant.

### 3.4. Step 4: Intelligent Filtering and Selection
This is where the system goes beyond a simple "top 3" list to provide a superior user experience, fulfilling the case study requirements for **explainability** and **diversity**. The system iterates through the ranked list and applies a set of rules to select the final recommendations:

*   **Rule 1: Prioritize New Content:** The algorithm heavily favors documents whose topics are **not** already in the user's `inferred_interests` list. This ensures we are suggesting fresh material.
*   **Rule 2: Ensure Topic Diversity:** To prevent recommending three articles all on the same sub-topic (e.g., three RAG files), the logic checks the "parent topic" (the part of the topic before the first slash, like `04_Implementation-RAG-Pipeline`). It avoids adding a new recommendation if its parent topic is already represented.
*   **Rule 3: Generate Dynamic Explanations:** Instead of a generic message, the explanation for *why* a document is recommended is generated dynamically based on its similarity score and whether the user has seen it before. The logic in the code explicitly checks thresholds to provide messages like "Highly relevant..." or "To broaden your knowledge...".
*   **Rule 4: Fill Remaining Slots:** If the above rules don't produce 3 recommendations (e.g., if the user is new or has seen most relevant content), the system backfills the remaining slots with the next-highest-scoring unseen items to ensure there are always suggestions.

This rule-based approach makes the recommendations feel reasoned, transparent, and genuinely helpful.