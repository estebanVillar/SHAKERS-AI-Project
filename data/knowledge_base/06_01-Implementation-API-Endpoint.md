# Implementation: The Backend API Endpoints

## 1. Overview
The backend is a Flask web server defined in `main.py`. It exposes a RESTful API that serves as the brain of the entire application. The Streamlit frontend is a "dumb" client that relies entirely on this API for all AI-driven functionality. All endpoints communicate using the JSON format for requests and responses.

---

## 2. Endpoint: `POST /api/query`
This is the primary workhorse endpoint of the application, responsible for handling a user's conversational turn.

*   **Purpose:** To receive a user query and chat history, orchestrate the full RAG pipeline, update the user's profile for future recommendations, and log the interaction for performance monitoring.
*   **Request Body (JSON):**
    ```json
    {
      "query": "The user's question as a string.",
      "user_id": "A unique identifier for the user.",
      "chat_history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    }
    ```
*   **Core Logic:** This endpoint's main job is to call `rag_chain.invoke()` and then orchestrate the user profile update and logging. For the full data flow, see **`01-Flow-Lifecycle-of-a-Query.md`**.
*   **Success Response (JSON):**
    ```json
    {
      "answer": "The AI-generated answer, complete with citations.",
      "sources": ["04_03-Implementation-Conversational-Chain", "..."]
    }
    ```

---

## 3. Endpoint: `POST /api/recommendations`
This endpoint provides the list of personalized document recommendations.

*   **Purpose:** To retrieve a list of recommended articles based on a user's calculated interest profile.
*   **Request Body (JSON):**
    ```json
    { "user_id": "The unique identifier for the user." }
    ```
*   **Core Logic:** It loads the user's profile, retrieves their `profile_vector`, and executes the recommendation algorithm against the `doc_embeddings_cache`. The full logic is detailed in **`05_02-Implementation-Recommendation-Algorithm.md`**.
*   **Success Response (JSON):**
    ```json
    {
      "recommendations": [
        {
          "title": "05_01-Implementation-User-Profile-Vector",
          "explanation": "Highly relevant to your interests..."
        }
      ]
    }
    ```

---

## 4. Endpoint: `POST /api/get_document`
This is a specialized, **optimized** endpoint that represents a key design decision for improving performance and reducing costs.

*   **Purpose:** To retrieve a summary of a *single, specific document* when its topic is already known (e.g., when a user clicks a recommendation button).
*   **Workflow & The "Why":**
    This endpoint deliberately **bypasses the entire expensive RAG chain**. Instead of history-aware retrieval and multi-document synthesis, it performs a much simpler, faster, and cheaper set of actions:
    1.  Directly looks up the requested `topic` in the `doc_embeddings_cache` to get its full content.
    2.  Invokes a lightweight LangChain summarization chain (`prompt | llm | StrOutputParser`) that simply asks the LLM to summarize the provided text.
*   **When It's Used:** The Streamlit frontend is programmed to call this endpoint—not `/api/query`—when a user types a query that directly matches the pattern `"Tell me about [topic]"`.
*   **Request Body (JSON):**
    ```json
    { "topic": "The exact topic string of the document to summarize." }
    ```
*   **Success Response (JSON):**
    ```json
    {
      "answer": "A comprehensive summary of the requested document.",
      "sources": ["the/requested/topic"]
    }
    ```