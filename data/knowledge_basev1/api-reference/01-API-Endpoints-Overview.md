# API Reference: Backend Endpoints

## 1. Overview

The backend is a Flask web server defined in `main.py`. It exposes a RESTful API that serves as the brain of the entire application. The Streamlit frontend is a "dumb" client that relies entirely on this API for all AI-driven functionality. All endpoints communicate using the JSON format for requests and responses.

---

## 2. Endpoint: `POST /api/query`

This is the primary workhorse endpoint of the application, responsible for handling a user's conversational turn.

*   **Purpose:** To receive a user query and chat history, orchestrate the full RAG pipeline, and return a generated answer. It also updates the user's profile for future recommendations.
*   **Request Body:**
    ```json
    {
      "query": "The user's question as a string",
      "user_id": "A unique identifier for the user",
      "chat_history": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
      ]
    }
    ```
*   **Workflow:**
    1.  Receives the request and validates the presence of required fields.
    2.  Invokes the complete `rag_chain` with the query and chat history.
    3.  Once a response is generated, it updates the user's profile in `user_profiles.json` by adding the new query to their history, adding the retrieved sources to their `inferred_interests`, and recalculating their `profile_vector`.
    4.  Logs the entire transaction (query, answer, sources, latency) to `query_logs.jsonl` for performance monitoring.
*   **Success Response:**
    ```json
    {
      "answer": "The AI-generated answer, complete with citations.",
      "sources": ["topic/of/source1", "topic/of/source2"]
    }
    ```
---

## 3. Endpoint: `POST /api/recommendations`

This endpoint provides the list of personalized document recommendations.

*   **Purpose:** To retrieve a list of recommended articles based on a user's calculated interest profile.
*   **Request Body:**
    ```json
    { "user_id": "The unique identifier for the user" }
    ```
*   **Workflow:**
    1.  Loads the `user_profiles.json` file.
    2.  Retrieves the specified user's `profile_vector` and `inferred_interests`.
    3.  Executes the recommendation algorithm: calculates cosine similarity against the `doc_embeddings_cache`, sorts, and applies filtering logic to generate the final list with explanations.
*   **Success Response:**
    ```json
    {
      "recommendations": [
        {
          "title": "recommendation-system/01-User-Profile...",
          "explanation": "Highly relevant to your interests..."
        },
        { "...": "..." }
      ]
    }
    ```
---

## 4. Endpoint: `POST /api/get_document`

This is a specialized, **optimized** endpoint that represents a key design decision for improving performance and reducing costs.

*   **Purpose:** To retrieve a summary of a *single, specific document* when its topic is already known.
*   **Workflow & Why It's Smart:**
    This endpoint deliberately **bypasses the entire expensive RAG chain**. Instead of history-aware retrieval and multi-document synthesis, it performs a much simpler, faster, and cheaper set of actions:
    1.  Directly looks up the requested `topic` in the `doc_embeddings_cache` to get its full content.
    2.  Invokes a lightweight LangChain summarization chain (`prompt | llm | StrOutputParser`) that simply asks the LLM to summarize the provided text.
*   **When It's Used:** The Streamlit frontend in `Chat_app.py` is programmed to call this endpoint—not `/api/query`—in two specific cases:
    1.  When a user clicks on a recommendation button.
    2.  When a user types a query that directly matches the pattern `"Tell me about [topic]"`.
*   **Request Body:**
    ```json
    { "topic": "The exact topic string of the document to summarize" }
    ```
*   **Success Response:**
    ```json
    {
      "answer": "A comprehensive summary of the requested document.",
      "sources": ["the/requested/topic"]
    }
    ```