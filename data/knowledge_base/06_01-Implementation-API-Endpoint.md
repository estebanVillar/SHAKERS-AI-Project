# Implementation: The Backend Flask API Endpoints

## 1. Overview
The backend is a Flask web server defined in `main.py`. It exposes a clean, well-defined RESTful API that serves as the command center for the entire application. The Streamlit frontend is a "thin client" that relies entirely on this API for all AI-driven functionality, state changes, and data retrieval. This architecture ensures a robust separation of concerns. All endpoints communicate using the standard JSON format for requests and responses.

---

## 2. Endpoint: `POST /api/query`
This is the primary workhorse endpoint of the application, responsible for handling a user's conversational turn and orchestrating the most complex logic.

*   **Purpose:** To receive a user query and chat history, invoke the full conversational RAG pipeline, update the user's profile with the new interaction data for future personalization, log the interaction for performance and cost monitoring, and return a cited, synthesized answer.
*   **Request Body (JSON):**
    ```json
    {
      "query": "The user's question as a string.",
      "user_id": "A unique identifier for the user session.",
      "chat_history": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
      ]
    }
    ```
*   **Core Logic:** This endpoint's main job is to call `rag_chain.invoke()` and then orchestrate the `_update_user_profile` and `log_query` utility functions. It also contains the "graceful failure" logic: if the RAG chain returns a "not found" message, this endpoint invokes a separate LLM chain to suggest relevant alternative questions. For the full data flow, see **`01-Flow-Lifecycle-of-a-Query.md`**.
*   **Success Response (JSON):**
    ```json
    {
      "answer": "The AI-generated answer, complete with in-text citations like [1] and a **Sources:** section.",
      "sources": ["04_03-Implementation-Conversational-Chain", "..."]
    }
    ```

---

## 3. Endpoint: `POST /api/recommendations`
This endpoint provides the list of personalized document recommendations.

*   **Purpose:** To retrieve a list of 2-3 recommended articles based on a user's dynamically calculated interest profile.
*   **Request Body (JSON):**
    ```json
    { "user_id": "The unique identifier for the user." }
    ```
*   **Core Logic:** It loads the user's profile, retrieves their `profile_vector` and `inferred_interests`, and executes the two-pass recommendation algorithm against the `doc_embeddings_cache`. The full logic is detailed in **`05_02-Implementation-Recommendation-Algorithm.md`**.
*   **Success Response (JSON):**
    ```json
    {
      "recommendations": [
        {
          "topic_id": "05_01-Implementation-User-Profile-Vector",
          "title": "Implementation User Profile Vector",
          "explanation": "Based on your recent interests, you might find this helpful."
        }
      ]
    }
    ```

---

## 4. Endpoint: `POST /api/get_document`
This is a specialized, **highly optimized** endpoint that represents a key design decision for improving performance and reducing cost.

*   **Purpose:** To retrieve a summary of a *single, specific document* when its topic is already known. This is used when a user clicks a recommendation button or a source link.
*   **The "Why" - A Performance Bypass:**
    This endpoint deliberately **bypasses the entire expensive conversational RAG chain**. Invoking the full chain (with history rephrasing, vector search, and multi-document synthesis) just to summarize one known document would be wasteful. Instead, this endpoint performs a much simpler, faster, and cheaper set of actions:
    1.  Directly looks up the requested `topic` in the `doc_embeddings_cache` to get its full content.
    2.  Invokes a lightweight, dedicated LangChain summarization chain (`prompt | llm | StrOutputParser`) that simply asks the LLM to summarize the provided text.
    3.  It still calls `_update_user_profile` to ensure the interaction is logged and contributes to the user's interest profile.
*   **When It's Used:** The Streamlit frontend is programmed with "intelligent routing" to call this endpoint—not `/api/query`—whenever a user's prompt directly matches a pattern like `"Tell me about [topic]"` or `"Please explain more about '[topic]'"`
*   **Request Body (JSON):**
    ```json
    { "topic": "The exact topic ID of the document to summarize." }
    ```
*   **Success Response (JSON):**
    ```json
    {
      "answer": "A comprehensive summary of the requested document, with a source citation.",
      "sources": ["the_requested_topic_id"]
    }
    ```

---

## 5. Endpoint: `POST /api/feedback`
A simple endpoint for collecting user feedback to enable future model improvements or analysis.

*   **Purpose:** To receive and log user feedback (helpful/unhelpful) on a specific AI-generated answer.
*   **Request Body (JSON):**
    ```json
    {
      "user_id": "The user's unique identifier.",
      "query": "The original query that prompted the answer.",
      "answer": "The answer being rated.",
      "score": 1 // (1 for helpful, -1 for unhelpful)
    }
    ```
*   **Core Logic:** The endpoint simply receives the data and appends it to `feedback_logs.jsonl` using the `log_feedback` utility.
*   **Success Response (JSON):**
    ```json
    { "status": "success", "message": "Feedback received" }
    ```