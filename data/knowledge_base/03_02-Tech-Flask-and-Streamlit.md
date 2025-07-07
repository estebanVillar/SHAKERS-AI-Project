# Technology: Flask and Streamlit, The Backend/Frontend Duo

## 1. The Analogy: A Professional Restaurant
Think of a full-service restaurant. To operate efficiently, it has two distinct but highly coordinated areas: The Kitchen and The Dining Room.

*   **The Kitchen (The Backend - Flask):** This is the engine room where the complex work happens. The chefs (our AI models, RAG chain, and business logic) take raw ingredients (user queries, data), follow precise recipes (our Python code), and produce a finished, complex product (a cited answer or a list of personalized recommendations). The kitchen is hidden from the customer and is optimized for power, process, efficiency, and scalability.

*   **The Dining Room (The Frontend - Streamlit):** This is the customer-facing area, focused entirely on the user experience. The waitstaff (our UI components) take orders from customers (user input), communicate those orders to the kitchen via a standardized system (API calls), and then present the finished dishes (AI responses) in an appealing, interactive, and easy-to-understand way. The dining room is optimized for presentation, user interaction, and ambiance.

This strict **separation of concerns** is a core principle of modern software engineering. Our project adheres to it rigorously, resulting in a system that is more scalable, maintainable, and easier to debug.

---

## 2. Our Backend Choice: Flask (`main.py`)
Flask was deliberately chosen as the "kitchen" for our application for several key reasons:

*   **Lightweight and Unopinionated:** Flask is a "micro-framework." It provides the bare essentials for building a web server and API (like routing and handling HTTP requests) and then gets out of the way. This gives us complete freedom and control to build our AI logic exactly as we see fit, without fighting against a heavy, restrictive framework with lots of built-in conventions.
*   **Perfect for APIs:** Flask is purpose-built for creating dedicated, stateless REST APIs. Our backend's only job is to receive a JSON request, perform a well-defined task, and return a JSON response. Flask excels at this simple, powerful pattern.
*   **Mature Ecosystem and Production-Ready:** While lightweight, Flask is incredibly mature and has a massive ecosystem of extensions. When deployed with a production-grade server like Gunicorn or Waitress, it is more than capable of handling high-traffic applications.

**In our project, `main.py` is a single Flask application that exposes a clean API with four key endpoints: `/api/query`, `/api/recommendations`, `/api/get_document`, and `/api/feedback`.**

---

## 3. Our Frontend Choice: Streamlit (`Chat_app.py`)
Streamlit was chosen as the "dining room" for its unique strengths, which make it exceptionally well-suited for building AI and data-centric applications:

*   **Incredible Speed of Development:** Streamlit allows us to build a rich, interactive, and beautiful user interface using only Python. There is no HTML, CSS, or JavaScript required. This enabled us to build the entire chat interface, session management, history, and the detailed metrics dashboard in a fraction of the time it would take with traditional web frameworks like React or Angular.
*   **Natively Data-Aware:** Streamlit has built-in, high-quality components for displaying dataframes, charts, and metrics (e.g., `st.dataframe`, `st.line_chart`, `st.metric`). This made the implementation of our "Metrics" page trivial and powerful.
*   **Simplified State Management:** Streamlit provides a simple yet effective session state management object (`st.session_state`). This is crucial for maintaining context in a chat application, allowing us to remember the user's ID, their current chat, and their entire chat history across interactions and page reruns.
*   **Theming:** As demonstrated in the final UI revamp, Streamlit's theming system (`config.toml`) allows for easy and comprehensive branding to match a specific visual identity.

**In our project, `Chat_app.py` is a pure UI layer. It contains zero AI logic and communicates exclusively with the Flask backend to get its content.**

---

## 4. How They Communicate: The API Contract
The frontend (Streamlit) and backend (Flask) communicate exclusively through standard HTTP requests, using the `requests` library in Python on the frontend.

1.  A user types a message in the Streamlit UI.
2.  Streamlit's Python script makes a `requests.post()` call to a specific URL on the Flask server (e.g., `http://127.0.0.1:5000/api/query`), sending a JSON payload.
3.  Flask receives the request, routes it to the correct Python function, processes it using the AI pipeline, and returns a JSON response.
4.  Streamlit receives this JSON, parses it, and updates the chat window and session state to display the new information to the user.
