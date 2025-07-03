# Core Concepts

To get the most out of the Shakers platform, it's helpful to understand the key concepts that power our services. This guide explains the "how" and "why" behind our intelligent systems, giving you the context you need to build robust and effective integrations.

---

## 1. Retrieval-Augmented Generation (RAG)

The heart of our question-answering service is a technology called **Retrieval-Augmented Generation (RAG)**. Unlike traditional Large Language Models (LLMs) that answer questions from their vast, general training data, our RAG system is designed for factual accuracy and relevance to the Shakers platform.

### How It Works

The RAG process ensures that every answer is grounded in our official knowledge base. Here’s a simplified breakdown of the lifecycle of a query:

![RAG Process Diagram](https://i.imgur.com/example-rag-flow.png) <!-- Fictional placeholder for a diagram -->

1.  **Query Input:** A user asks a question, like *"How do I resolve a payment dispute?"*

2.  **Retrieval Step (The "R"):** Instead of immediately asking an LLM to answer, the system first performs a search. It **retrieves** the most relevant chunks of information from our private, curated **Knowledge Base** (more on this below). This search is powered by vector embeddings, allowing for semantic understanding of the query's intent, not just keyword matching.

3.  **Augmentation Step (The "A"):** The original user query is then **augmented** (combined) with the retrieved information. This bundle of context and the original question is packaged into a precise prompt for the LLM.

4.  **Generation Step (The "G"):** Finally, the LLM **generates** a human-readable answer. Crucially, it is instructed to formulate its response *exclusively* based on the provided context. It synthesizes the key points from the source documents into a clear and concise answer.

### Why RAG is a Game-Changer

*   **Minimizes "Hallucinations":** Because the LLM is constrained to a specific set of source documents, it cannot "make up" facts or provide information from outside the Shakers ecosystem. This ensures the answers are reliable and trustworthy.
*   **Always Up-to-Date:** As we update our knowledge base with new features or policies, the RAG system automatically provides answers based on the latest information, without needing to retrain a massive model.
*   **Verifiable and Transparent:** Every answer comes with references to the source documents. This allows users (and developers) to trace the origin of the information, building trust and providing pathways for deeper learning.

---

## 2. Personalized Recommendation Service

While the RAG service is reactive (it answers direct questions), the **Personalized Recommendation Service** is proactive. Its goal is to guide users by anticipating their needs based on their behavior.

### How It Builds a User Profile

The system creates a temporary, dynamic user profile based on two key inputs:

1.  **Current Query:** The user's most recent question provides immediate context.
2.  **Query History:** A list of the user's previous queries reveals their broader interests and journey on the platform.

For example, a user who asks *"What are typical rates for Python developers?"* followed by *"How do I write a good project brief?"* is clearly in the initial stages of hiring.

### The Recommendation Process

1.  **Topic Identification:** The system analyzes the user profile to identify recurring themes and areas of interest (e.g., "hiring," "payments," "developer skills").

2.  **Candidate Selection:** It then searches our resource library (which includes articles, guides, and tutorials) for content matching these topics.

3.  **Filtering & Diversification:** This is the smart part. The system filters the candidate list to ensure the recommendations are:
    *   **Relevant:** Directly related to the user's inferred interests.
    *   **Novel:** Prioritizes resources the user has not previously been shown.
    *   **Diverse:** Avoids suggesting multiple articles on the exact same niche topic, instead providing a well-rounded set of next steps.

4.  **Explainable Output:** Each recommendation is delivered with a brief explanation of *why* it is being suggested, making the experience transparent and more helpful for the user.

---

## 3. The Knowledge Base

The **Knowledge Base** is the foundational pillar upon which our entire RAG system is built. It is the single source of truth for all information about the Shakers platform.

*   **What it is:** A private, curated collection of technical documents, policy guides, feature explanations, and FAQs. These are stored in a simple, structured format (Markdown) that is easy for us to update and maintain.

*   **Its Role:**
    *   **For the RAG Service:** It is the *only* place the RAG system looks for information during the "Retrieval" step. The quality, clarity, and comprehensiveness of our Knowledge Base directly correlate to the quality of the generated answers.
    *   **For Recommendations:** Many of the articles and guides suggested by the Recommendation Service are also part of this knowledge base.

By understanding these core concepts, you are now better equipped to design powerful integrations and leverage the full potential of the Shakers Intelligent Support System.

### Next Steps

*   Ready to see these concepts in action? Dive into the **[API Reference](./04-api-reference/01-overview.md)** for detailed endpoint specifications.
*   Want to see how to put this all together? Check out our tutorial on **[Building a Support Chatbot](./05-guides/01-building-a-support-chatbot.md)**.