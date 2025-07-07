# Implementation: The Recommendation Algorithm

## 1. Overview
Once the system has built a user profile with a dynamic interest vector, it can generate personalized recommendations. The goal of this system is not merely to suggest popular or random documents. It is designed to proactively offer 2-3 articles that are **highly relevant** to the user's current train of thought, **diverse** in their subject matter, and preferably **new** to the user. This entire process is encapsulated in the `/api/recommendations` endpoint and its corresponding `handle_recommendations` function in `main.py`.

---

## 2. A Critical Optimization: The `doc_embeddings_cache`
A naive approach to recommendations would be to re-read all markdown files and re-embed their content every single time a recommendation is requested. This would be incredibly slow, computationally expensive, and would incur significant API costs, making real-time recommendations impossible.

To solve this, our project implements a crucial startup optimization. When the Flask server in `main.py` first launches, the `initialize_rag_pipeline` function performs a one-time process:
1.  It iterates through every large "parent document" stored in the `docstore`.
2.  For each document, it embeds the **entire page content** using our `models/embedding-001` model.
3.  It stores this information in a Python dictionary in memory called `doc_embeddings_cache`. This dictionary maps each document's unique `topic` ID to a dictionary containing its full `content` and its pre-computed `embedding`.

**The Benefit:** This one-time, upfront computation means that when a recommendation request comes in, the system has instant, in-memory access to the vector representation of every document in the knowledge base. The recommendation process becomes a series of lightning-fast lookups and calculations rather than a slow, expensive I/O and embedding operation, ensuring the API endpoint responds in milliseconds.

---

## 3. The Recommendation Algorithm: A Step-by-Step Guide

The algorithm follows a structured process of scoring, ranking, and intelligent filtering.

### 3.1. Step 1: Fetch the User's Current State
The `handle_recommendations` function begins by loading the `user_profiles.json` file. It retrieves the specific user's `profile_vector` (their current center of interest) and their list of `inferred_interests` (a set of topics they've already seen based on RAG sources).

### 3.2. Step 2: Calculate Similarity Scores
The algorithm then iterates through every single document in the pre-computed `doc_embeddings_cache`. For each document, it calculates the **cosine similarity** between the user's `profile_vector` and that document's embedding. This produces a numerical score (from -1 to 1) of thematic relevance for every single document in the knowledge base relative to the user's aggregated interests.

*For a detailed explanation of this metric, see **`02_03-Concepts-Vector-Embeddings.md`***.

### 3.3. Step 3: Rank by Relevance
All documents are then placed in a list, and this list is sorted in descending order based on their similarity score. This creates a ranked list of all documents, from most thematically relevant to least.

### 3.4. Step 4: Intelligent Filtering and Selection (The Two-Pass System)
This is where the system goes beyond a simple "top 3" list to provide a superior user experience, directly fulfilling the case study requirements for **explainability** and **diversity**. The system uses a two-pass approach to select the final recommendations from the ranked list:

*   **Pass 1: The "Perfect" Recommendation Pass:**
    The system iterates through the ranked list, looking for recommendations that meet three strict criteria:
    1.  **Must be New:** The topic must **not** already be in the user's `inferred_interests` list.
    2.  **Must be Diverse:** To prevent recommending three articles all on the same sub-topic (e.g., three RAG implementation files), the logic extracts a "parent topic" (e.g., `04_Implementation-RAG-Pipeline` from `04_01-...`). It ensures that it doesn't add a new recommendation if its parent topic is already represented in the recommendations list.
    3.  **Must be Relevant:** This is guaranteed by iterating through the list in sorted order.

*   **Pass 2: The "Backfill" Pass:**
    If the first pass does not yield the maximum number of recommendations (e.g., if the user has already seen all the diverse, relevant topics), this second pass iterates through the ranked list again. It simply looks for the highest-scoring topics that have not yet been recommended and are not in the user's "seen" list, filling the remaining slots. This ensures we always try to provide a full set of suggestions.

*   **Dynamic Explanations:** The explanation for *why* a document is recommended is generated dynamically. In our implementation, a different, hardcoded explanation is used for Pass 1 ("Based on your recent interests...") vs. Pass 2 ("This related topic might also be of interest...") to provide some variety.

This rule-based, two-pass approach makes the recommendations feel reasoned, transparent, and genuinely helpful in guiding the user to new, relevant information.