# Frontend and Evaluation Part 1: The Streamlit Frontend

## 1. The Role of the Frontend: A Pure UI Layer

The frontend, built using Streamlit in the `app/Chat_app.py` file, serves as the user's interactive gateway to the AI system. Its design philosophy is to be a "thin client" or pure User Interface (UI) layer. It contains no core AI logic itself; instead, it is responsible for three primary tasks:

1.  **Rendering the User Interface:** Drawing the chat window, sidebar, buttons, and metrics dashboard.
2.  **Managing Application State:** Keeping track of chat histories, the current user's ID, and which page is being viewed.
3.  **Communicating with the Backend:** Making structured API calls to the Flask server to fetch all dynamic and AI-generated content.

This separation of concerns is a robust software engineering practice that makes the system easier to develop, debug, and scale.

---

## 2. Session State Management: The Brain of the UI

Streamlit reruns the entire script on almost every user interaction. To maintain a persistent experience (like keeping chat history visible), the application relies heavily on `st.session_state`. This is a dictionary-like object that persists across reruns.

The `initialize_session` function ensures the following critical variables are always present:

*   **`st.session_state.current_page`**: Manages navigation between the 'chat' view and the 'metrics' dashboard.
*   **`st.session_state.user_id`**: A unique identifier is created for each user on their first visit (using `f"user_{datetime.now().timestamp()}"`) and then persists for the duration of their browser session. This is the key that links the frontend user to their profile on the backend.
*   **`st.session_state.chat_sessions`**: A dictionary that stores the entire history of all chats. The keys are `chat_id`s, and the values are objects containing the chat `title` and a list of `messages`. This allows users to switch between past conversations seamlessly.
*   **`st.session_state.current_chat_id`**: Points to the key of the currently active chat in the `chat_sessions` dictionary. The `new_chat` function creates a new entry and sets this pointer.
*   **`st.session_state.new_query`**: A special state variable used as a communication bridge. When a recommendation button is clicked, its callback function (`set_new_query`) places the query text into this variable. The main script loop detects this and processes it as if the user had typed it, allowing buttons to trigger queries.

---

## 3. Intelligent Frontend Routing: An Important Optimization

A standout feature of the frontend architecture is its ability to perform **intelligent routing**. The UI is smart enough to know which backend endpoint is the most efficient one to call for a given query. This logic is implemented just before the API call is made.

1.  **The Check:** The frontend uses a regular expression (`re.search(r"Tell me about\s+(.+)", prompt, re.IGNORECASE)`) to check if the user's input is a direct request for a specific document summary.

2.  **The Two Paths:**
    *   **If it's a direct request** (e.g., from a recommendation button click like "Tell me about recommendation-system/02..."), the frontend makes a `POST` request to the specialized, faster, and cheaper `/api/get_document` endpoint.
    *   **For all other queries** (general questions, follow-ups), it calls the standard, more powerful `/api/query` endpoint, which invokes the full conversational RAG chain.

**Why this matters:** This client-side decision significantly improves the perceived performance and efficiency of the application. Simple summary requests are fulfilled nearly instantly, enhancing the user experience, while complex queries are still handled with the full power of the RAG system.

---

## 4. UI Components and Backend Communication

*   **Chat History Display:** The application iterates through the messages in the current session (`current_chat["messages"]`) and displays them using `st.chat_message`.
*   **Recommendation Buttons:** After an assistant response, if recommendations are available, the frontend dynamically creates a set of columns (`st.columns`) and renders each recommendation as a clickable `st.button`. The `on_click` argument is tied to the `set_new_query` callback, enabling the button-to-query mechanism.
*   **API Communication:** The `requests` library is used for all communication with the Flask backend. The frontend includes robust error handling, specifically a `try...except requests.exceptions.ConnectionError` block. This allows the application to fail gracefully and display a helpful error message (`"Error: Could not connect to the backend server..."`) if the Flask app isn't running, which is crucial for a smooth user and evaluation experience.