
# Project Overview: The Self-Documenting AI Assistant

## 1. Core Mission and Philosophy
This project implements an intelligent technical support system designed for a unique purpose: to answer questions about its own architecture, design choices, and functionality. It is a "meta" chatbot that uses a provided knowledge base—the very documentation you are reading—to explain precisely how it works.

The core philosophy is to demonstrate a robust, production-ready, end-to-end AI system that is not only functional but also transparent, well-engineered, and self-documenting. The goal is to provide an evaluator with a tool to explore the project's complexities through natural language, creating an interactive and in-depth evaluation experience that goes far beyond simply reading code.

The system's objectives are twofold, as specified by the case study:
1.  **Answer Technical Questions:** Accurately respond to user queries about its construction using a sophisticated Retrieval-Augmented Generation (RAG) pipeline.
2.  **Proactively Recommend Resources:** Suggest relevant articles from this knowledge base based on the user's dynamically inferred interests, guiding them toward a fuller, more comprehensive understanding of the project.

---

## 2. High-Level System Architecture
The system is architected with a strict separation of concerns between the user interface and the core AI logic, a standard and scalable pattern for modern web applications.

*   **Frontend (Streamlit):** A pure user interface layer responsible for rendering the chat window, managing user sessions and chat history, displaying a real-time metrics dashboard, and handling user interactions like button clicks and feedback submission. It makes structured API calls to the backend to get all AI-generated content and recommendations. It contains **zero** core AI logic.

*   **Backend (Flask):** A robust API server that houses all complex AI logic. It handles the one-time document ingestion pipeline, the live conversational RAG chain, dynamic user profile management, personalized recommendation generation, and performance/cost logging. This separation ensures that intensive AI processing does not block the UI and that the backend can be scaled, updated, and maintained independently.

---

## 3. Technology Stack and Key Components
The selection of technologies was driven by the goals of rapid development, proven robustness in production environments, and leveraging state-of-the-art AI tooling.

*   **Backend Framework:**
    *   **Flask:** Chosen for its lightweight, modular, and unopinionated nature. It is perfect for creating a clean, dedicated REST API server for the AI logic, without the overhead of a larger framework.

*   **AI/LLM Orchestration:**
    *   **LangChain:** The primary framework used to "chain" together all the components of the RAG and recommendation systems. Its high-level abstractions for retrievers, prompts, and models drastically accelerate development while providing the flexibility to implement advanced strategies like the `ParentDocumentRetriever` and `HistoryAwareRetriever`.

*   **Generative AI Models (Google Gemini):**
    *   **`gemini-1.5-flash-latest`:** Used as the core Large Language Model (LLM) for reasoning, answering questions, and summarizing documents. It was chosen for its exceptional balance of high performance, long context window, multi-lingual capability, and low latency, which is critical for a responsive user experience.
    *   **`models/embedding-001`:** The workhorse model for converting text (documents and user queries) into numerical vectors (embeddings). This is the absolute backbone of all semantic search and similarity calculations in the system.

*   **Retrieval and Data Storage:**
    *   **FAISS (Facebook AI Similarity Search):** An extremely efficient library for vector similarity search. It serves as the project's **Vectorstore**, indexing all the document chunks for fast, sub-second retrieval.
    *   **In-Memory Store & Pickle:** The `ParentDocumentRetriever` uses a simple in-memory key-value store for the parent documents. This, along with the FAISS index, is cached to disk using `pickle`, ensuring near-instantaneous application startup times after the initial one-time setup.

*   **Frontend Framework:**
    *   **Streamlit:** Chosen for its unparalleled ability to create beautiful, interactive data and chat applications with pure Python. This allowed for the rapid development of a polished UI, including the metrics dashboard, without writing a single line of HTML, CSS, or JavaScript. Theming capabilities were used to align the UI with a specific brand identity.

---

## 4. Your Guide: The Knowledge Base Roadmap
This knowledge base is structured to guide you from the high-level flow down to fine-grained implementation details. **The recommended starting point for a deep dive is `01-Flow-Lifecycle-of-a-Query.md`**, as it traces a single user request through the entire system.

The file paths themselves are programmatically used as citation topics by the chatbot.

*   **`01-Flow-Lifecycle-of-a-Query.md`**: Traces a single user request from the browser, through the API, to the AI, and back.
*   **Section 02 (Concepts):** Explains foundational AI concepts like RAG, LLMs, and Vector Embeddings in simple, analogy-driven terms. It discusses the "why" behind these technologies.
*   **Section 03 (Technology):** Provides an overview of the key libraries and frameworks used, like LangChain, Flask, and FAISS, and explains our rationale for choosing each one.
*   **Sections 04-06 (Implementation):** These sections are the core of the documentation, containing detailed, code-level explanations of how the RAG pipeline, recommendation system, API, frontend, and evaluation suite were built.

---

## 5. Main Topics Available
This knowledge base is organized into several key areas to provide a comprehensive understanding of the project. You can ask about:
*   **The Project Flow:** How a query travels through the system from start to finish.
*   **Core AI Concepts:** Foundational ideas like RAG, LLMs, and Vector Embeddings.
*   **The Technology Stack:** Details on key libraries like LangChain, Flask, Streamlit, and FAISS.
*   **The RAG Pipeline Implementation:** How we load, index, and retrieve information, including the Parent Document Retriever strategy.
*   **The Recommendation System:** The logic behind user profiles, interest vectors, and personalized suggestions.
*   **The Backend and Frontend:** The architecture of the Flask API and the Streamlit user interface, including state management and theming.
*   **Metrics and Evaluation:** How the system's performance, cost, and quality are measured and validated.