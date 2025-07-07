# Project Overview: The Self-Documenting AI Assistant

## 1. Core Mission and Philosophy
This project implements an intelligent technical support system designed for a unique purpose: to answer questions about its own architecture, design choices, and functionality. It is a "meta" chatbot that uses a provided knowledge base—the very documentation you are reading—to explain how it works.

The core philosophy is to demonstrate a robust, end-to-end AI system that is not only functional but also transparent and self-documenting. The goal is to provide an evaluator with a tool to explore the project's complexities through natural language, creating an interactive and in-depth evaluation experience.

The system's objectives are twofold, as specified by the case study:
1.  **Answer Technical Questions:** Accurately respond to user queries about its construction using a Retrieval-Augmented Generation (RAG) pipeline.
2.  **Proactively Recommend Resources:** Suggest relevant articles from this knowledge base based on the user's inferred interests, guiding them toward a fuller understanding of the project.

---

## 2. High-Level System Architecture
The system is architected with a clear separation of concerns between the user interface and the core AI logic, a standard practice for building scalable web applications.

*   **Frontend (Streamlit):** A pure user interface layer responsible for rendering the chat window, managing user sessions, and displaying performance metrics. It makes API calls to the backend to get all AI-generated content.
*   **Backend (Flask):** A robust API server that houses all the complex AI logic. It handles document ingestion, the RAG chain, user profile management, and recommendation generation. This separation ensures that the AI processing does not block the UI and can be scaled independently.

---

## 3. Technology Stack and Key Components
The selection of technologies was driven by the goals of rapid development, proven robustness, and leveraging state-of-the-art AI tooling.

*   **Backend Framework:**
    *   **Flask:** Chosen for its lightweight, modular, and unopinionated nature, making it perfect for creating a clean, dedicated API server for AI logic.

*   **AI/LLM Orchestration:**
    *   **LangChain:** The primary framework used to "chain" together all the components of the RAG and recommendation systems. Its high-level abstractions for retrievers, prompts, and models drastically accelerate development while maintaining flexibility.

*   **Generative AI Models (Google Gemini):**
    *   **`gemini-1.5-flash-latest`:** Used as the core Large Language Model (LLM) for reasoning, answering questions, and summarizing documents. It was chosen for its excellent balance of performance, long context window, and low latency.
    *   **`models/embedding-001`:** Used for converting text (documents and user queries) into numerical vectors (embeddings). This is the backbone of all semantic search and similarity calculations.

*   **Retrieval and Data Storage:**
    *   **FAISS (Facebook AI Similarity Search):** An extremely efficient library for vector similarity search. It serves as the project's **Vectorstore**, indexing all the document chunks for fast retrieval.
    *   **In-Memory Store & Pickle:** Used for caching the RAG components and pre-computed embeddings to disk, ensuring near-instantaneous startup times after the initial one-time setup.

*   **Frontend Framework:**
    *   **Streamlit:** Chosen for its ability to create beautiful, interactive data and chat applications with pure Python, allowing for rapid UI development that is tightly integrated with the backend logic.

---

## 4. Your Guide: The Knowledge Base Roadmap
This knowledge base is structured to guide you from the high-level flow down to fine-grained implementation details. **The recommended starting point for a technical deep dive is `01-Flow-Lifecycle-of-a-Query.md`**.

The file paths themselves are programmatically used as citation topics by the chatbot.

*   **`01-Flow-Lifecycle-of-a-Query.md`**: Traces a single user request from the browser to the AI and back.
*   **Section 02 (Concepts):** Explains foundational AI concepts like RAG, LLMs, and Vector Embeddings in simple terms.
*   **Section 03 (Technology):** Provides an overview of the key libraries and frameworks used, like LangChain and FAISS.
*   **Sections 04-06 (Implementation):** Contain detailed, code-level explanations of how the RAG pipeline, recommendation system, API, and frontend were built.

## 5. Main Topics Available
This knowledge base is organized into several key areas to provide a comprehensive understanding of the project. You can ask about:
*   **The Project Flow:** How a query travels through the system from start to finish.
*   **Core AI Concepts:** Foundational ideas like RAG, LLMs, and Vector Embeddings.
*   **The Technology Stack:** Details on key libraries like LangChain, Flask, Streamlit, and FAISS.
*   **The RAG Pipeline Implementation:** How we load, index, and retrieve information.
*   **The Recommendation System:** The logic behind user profiles and personalized suggestions.
*   **The Backend and Frontend:** The architecture of the API and the Streamlit user interface.
*   **Metrics and Evaluation:** How the system's performance and quality are measured.