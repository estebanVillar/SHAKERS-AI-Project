# The Lifecycle of a Query: From Browser to AI and Back

## 1. Introduction
This document provides a step-by-step trace of a single user's question, showing how every component in this project works in concert. We'll follow the data flow from the moment a user hits 'Enter' in the chat to the moment the AI's fully-formed response and personalized recommendations appear on screen. Understanding this flow is the key to understanding the entire system.

---

## 2. The Starting Point: The Frontend (`Chat_app.py`)
The journey begins in the Streamlit user interface, which is responsible for capturing user input and directing traffic.

*   **Capture Input:** The `st.chat_input` function (or a button click callback) in `Chat_app.py` captures the raw text `prompt` from the user.
*   **Intelligent Routing (A Key Optimization):** Before sending the request, the frontend performs a crucial optimization. It uses a regular expression to check if the prompt is a simple request for a document summary (e.g., `"Please explain more about 'The RAG Pipeline Implementation'"`). This check determines which backend endpoint is most efficient.
    *   **Path A (Full RAG for Complex Queries):** For a general or ambiguous question (e.g., "Why use FAISS?"), the frontend makes a `POST` request to the `/api/query` endpoint. The JSON payload includes the `query`, `user_id`, and `chat_history`.
    *   **Path B (Optimized Summary for Direct Requests):** For a direct request, it calls the specialized, faster `/api/get_document` endpoint. This avoids the cost and latency of the full conversational RAG chain for simple, targeted requests, directly improving user experience.
*   **For more details on the UI architecture and this routing logic, see `06_02-Implementation-Frontend-Architecture.md`**.

---

## 3. The Gateway: The Backend API (`main.py`)
The request arrives at the Flask server, which acts as the application's central nervous system.

*   The `@app.route('/api/query')` decorator directs the incoming request to the `handle_query` function.
*   This function first validates the incoming JSON data to ensure it contains a `query` and `user_id`. It then starts a timer (`g.start_time`) to precisely measure server-side latency for our performance metrics.

---

## 4. The Core Logic: The Conversational RAG Chain (`rag_pipeline.py`)
The `handle_query` function's primary job is to call the `rag_chain.invoke()` method. This single call orchestrates a sophisticated, multi-step process defined in `rag_pipeline.py`:

*   **Step 4a: Rephrase the Question (Contextualization):** The chain's first component is a `HistoryAwareRetriever`. It takes the chat history and the new, potentially ambiguous question (e.g., "Why?") and uses an LLM to rephrase it into a complete, standalone question (e.g., "Why is the Parent Document Retriever a better strategy than simple chunking?"). This is essential for fluid, natural conversation.
*   **Step 4b: Retrieve Documents (Precision Search):** This rephrased question is then passed to our `ParentDocumentRetriever`. It embeds the question into a vector and performs a similarity search in the **FAISS** vector store to find the most relevant *small child chunks*. It then fetches the corresponding *large parent chunks* to provide full context.
*   **Step 4c: Generate the Answer (Synthesis & Guardrails):** The retrieved parent documents are "stuffed" into the context of a carefully engineered prompt. This prompt, along with the original question, is sent to the `gemini-1.5-flash` LLM. The prompt acts as a strict contract, instructing the LLM to synthesize the final, cited answer *exclusively* from the provided text and to respond gracefully if the answer isn't present.
*   **To understand the theory of RAG, see `02_01-Concepts-Intro-to-RAG.md`. For the exact implementation of this chain, read `04_03-Implementation-Conversational-Chain.md`**.

---

## 5. Learning & Personalization (`main.py`)
Immediately after a valid, sourced answer is generated, the `handle_query` function updates the user's profile in `user_profiles.json` to improve future interactions.

*   The raw query is added to the user's `query_history`.
*   The `sources` retrieved by the RAG chain are added to the user's `inferred_interests`, marking these topics as "seen."
*   The user's `profile_vector` is updated using a moving average, blending their existing interest vector with the vector of the new query. This subtly shifts their interest profile in real-time.
*   **The logic for this is detailed in `05_01-Implementation-User-Profile-Vector.md`**.

---

## 6. Proactive Assistance: The Recommendation Flow
The user experience doesn't end with an answer. To guide the user, the system provides proactive recommendations.

*   After the main answer is displayed, the `Chat_app.py` frontend makes a *second, separate API call* to the `/api/recommendations` endpoint.
*   The backend's `handle_recommendations` function uses the user's just-updated `profile_vector` to calculate its cosine similarity against the pre-computed embeddings of all documents in the knowledge base.
*   It then applies a set of intelligent filtering rules (e.g., prioritize unseen topics, ensure diversity across categories) to select and return the top 2-3 most relevant articles with dynamically generated explanations.
*   **For the complete algorithm, see `05_02-Implementation-Recommendation-Algorithm.md`**.

---

## 7. The Finish Line: Rendering the Final UI
The Streamlit frontend receives the JSON responses from both the query and recommendation API calls and renders the final UI:
1.  The assistant's answer, including formatted sources, is displayed using `st.chat_message`.
2.  Feedback buttons (👍/👎) are rendered next to the new answer.
3.  The personalized recommendations are displayed as clickable, themed buttons at the bottom of the chat, ready to start the cycle anew.
