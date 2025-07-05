# Technology: Flask and Streamlit, The Frontend/Backend Duo

## 1. The Analogy: A Restaurant
Think of a full-service restaurant. There are two distinct areas that must work together seamlessly:

*   **The Kitchen (The Backend - Flask):** This is where the complex work happens. The chefs (our AI models and logic) take raw ingredients (data), follow recipes (our code), and produce a finished product (an answer or recommendation). The kitchen is optimized for power, efficiency, and process. Customers never see the kitchen's inner workings.
*   **The Dining Room (The Frontend - Streamlit):** This is the customer-facing area. The waiters (our UI) take orders from customers (user queries), deliver them to the kitchen, and present the finished dishes (AI responses) in an appealing way. The dining room is optimized for user experience, presentation, and interaction.

This separation is a core principle of modern web development, and our project adheres to it strictly.

---

## 2. Our Backend Choice: Flask (`main.py`)
Flask was chosen as the "kitchen" for our application for several reasons:

*   **Lightweight and Unopinionated:** Flask is a "micro-framework." It provides the bare essentials for building a web server and API (like routing and handling requests) and gets out of the way. This gives us complete control to build our AI logic exactly as we want, without fighting a heavy, restrictive framework.
*   **Ideal for APIs:** Flask is perfect for creating dedicated, stateless REST APIs. Our backend's only job is to receive a JSON request, perform a task, and return a JSON response. Flask excels at this.
*   **Mature Ecosystem:** While lightweight, Flask has a massive ecosystem of extensions, so if we needed to add more complex features later (like database integration or advanced user authentication), it would be straightforward.

**In our project, `main.py` is a single Flask application that exposes three key API endpoints: `/api/query`, `/api/recommendations`, and `/api/get_document`.**

---

## 3. Our Frontend Choice: Streamlit (`Chat_app.py`)
Streamlit was chosen as the "dining room" for its unique strengths, particularly for AI and data-centric applications:

*   **Speed of Development:** Streamlit allows us to build a beautiful, interactive user interface using only Python. There is no HTML, CSS, or JavaScript required. This let us build the entire chat interface, history, and metrics dashboard in a fraction of the time it would take with traditional web frameworks.
*   **Built for Data:** Streamlit has native components for displaying dataframes, charts, and metrics (`st.dataframe`, `st.line_chart`, `st.metric`), making our "Metrics" page incredibly easy to implement.
*   **State Management:** It provides a simple yet effective session state (`st.session_state`) mechanism, which is crucial for maintaining context in a chat application (like remembering the user's ID and chat history across interactions).

**In our project, `Chat_app.py` is a pure UI layer. It contains zero AI logic and simply communicates with the Flask backend to get all its content.**

---

## 4. How They Communicate
The frontend (Streamlit) and backend (Flask) communicate exclusively through HTTP requests, using the `requests` library in Python.

1.  A user types a message in the Streamlit UI.
2.  Streamlit's Python script makes a `requests.post()` call to a specific URL on the Flask server (e.g., `http://127.0.0.1:5000/api/query`).
3.  Flask receives the request, processes it, and returns a JSON response.
4.  Streamlit receives the JSON, parses it, and updates the chat window to display the answer.