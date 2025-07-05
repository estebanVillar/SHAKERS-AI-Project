# The Lifecycle of a Query: From Browser to AI and Back

## 1. Introduction
This document traces the complete journey of a user's question, showing how every component in this project works together. We'll follow the data flow from the moment a user hits 'Enter' in the chat to the moment the AI's response and personalized recommendations appear on screen.

---

## 2. The Starting Point: The Frontend (`Chat_app.py`)
The journey begins in the Streamlit user interface.

*   **Capture Input:** The `st.chat_input` function in `Chat_app.py` captures the raw text `prompt` from the user.
*   **Intelligent Routing:** Before sending the request, the frontend performs a crucial optimization. It uses a regular expression to check if the prompt is a simple request for a document summary (e.g., `"Tell me about [topic]"`).
    *   **Path A (Full RAG):** For a general or complex question, the frontend makes a `POST` request to the `/api/query` endpoint. The JSON payload includes the `query`, `user_id`, and `chat_history`.
    *   **Path B (Optimized Summary):** For a direct request, it calls the specialized, faster `/api/get_document` endpoint. This avoids the cost and latency of the full RAG chain for simple requests.
*   **For more details on the UI, see `06_02-Implementation-Frontend-Architecture.md`**.

---

## 3. The Gateway: The Backend API (`main.py`)
The request arrives at the Flask server, which acts as the application's brain.

*   The `@app.route('/api/query')` decorator directs the incoming request to the `handle_query` function.
*   This function first validates the incoming data and starts a timer to measure latency for our performance metrics.

---

## 4. The Core Logic: The Conversational RAG Chain
The `handle_query` function's primary job is to call the `rag_chain.invoke()` method. This single call orchestrates a sophisticated, multi-step process defined in `main.py`:

*   **Step 4a: Rephrase the Question:** The chain's first component is a `HistoryAwareRetriever`. It takes the chat history and the new, potentially ambiguous question (e.g., "Why?") and uses an LLM to rephrase it into a complete, standalone question (e.g., "Why is the Parent Document Retriever a better strategy?").
*   **Step 4b: Retrieve Documents:** This rephrased question is then passed to our `ParentDocumentRetriever`. It embeds the question into a vector and performs a similarity search in the **FAISS** vector store to find the most relevant document chunks.
*   **Step 4c: Generate the Answer:** The retrieved documents are "stuffed" into the context of a carefully engineered prompt. This prompt, along with the original question, is sent to the `gemini-1.5-flash` LLM, which synthesizes the final, cited answer according to the strict rules in the prompt.
*   **To understand the theory, see `02_01-Concepts-Intro-to-RAG.md`. For the exact implementation, read `04_03-Implementation-Conversational-Chain.md`**.

---

## 5. Learning & Personalization
After a valid answer is generated, the `handle_query` function immediately updates the user's profile in `user_profiles.json` to improve future interactions.

*   The new query is added to the user's history.
*   The `sources` retrieved by the RAG chain are added to the user's `inferred_interests`.
*   The user's `profile_vector` is updated by averaging their existing vector with the vector of the new query, subtly shifting their interest profile.
*   **The logic for this is detailed in `05_01-Implementation-User-Profile-Vector.md`**.

---

## 6. Proactive Assistance: The Recommendation Flow
The user experience doesn't end with an answer.

*   Immediately after displaying the answer, the `Chat_app.py` frontend makes a *second, separate API call* to the `/api/recommendations` endpoint.
*   The backend's `handle_recommendations` function uses the user's just-updated `profile_vector` to calculate its cosine similarity against the pre-computed embeddings of all documents in the knowledge base.
*   It then applies a set of filtering rules (e.g., prioritize unseen topics, ensure diversity) to select and return the top 2-3 most relevant articles with explanations.
*   **For the complete algorithm, see `05_02-Implementation-Recommendation-Algorithm.md`**.

---

## 7. The Finish Line: Rendering the Final UI
The Streamlit frontend receives the response from both API calls and renders the final UI:
1.  The assistant's answer is displayed using `st.chat_message`.
2.  The personalized recommendations are displayed as clickable buttons using `st.button`.