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

## 4. Knowledge Base and Project Roadmap

This knowledge base is structured to guide you from high-level concepts to fine-grained implementation details. The file paths themselves are used as citation topics by the chatbot.

*   `knowledge_base/`
    *   `00-Project-Overview.md`: **(You are here)**
    *   `rag-pipeline/`: Contains deep dives into how the RAG system ingests data and generates answers.
    *   `recommendation-system/`: Explains the logic behind user profiling and personalized recommendations.
    *   `api-reference/`: A technical guide to the backend API endpoints.
    *   `frontend-and-evaluation/`: Details on the Streamlit UI and the performance evaluation framework.