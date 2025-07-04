# RAG Pipeline Part 1: Ingestion and Indexing

## 1. Overview

The foundation of any RAG system is its ability to efficiently process and index its knowledge base. The ingestion pipeline is a one-time process (with intelligent caching) that converts the raw markdown documents in this knowledge base into a searchable, high-performance index. This process is crucial for enabling the chatbot to find relevant information quickly.

The process follows these key steps: **Load -> Split -> Embed -> Store**.

---

## 2. Document Loading

The pipeline begins by loading all source documents from the `data/knowledge_base` directory.

*   **Component Used:** `langchain_community.document_loaders.DirectoryLoader`
*   **Implementation Details:** The loader is configured to find all `**/*.md` files, ensuring it recursively scans the entire directory structure. It uses multithreading (`use_multithreading=True`) for faster I/O operations and is set to use `utf-8` encoding to prevent issues with special characters.

---

## 3. The Parent Document Retriever (PDR) Strategy

A critical architectural decision was the choice of retrieval strategy. Instead of using a basic text splitter, this project implements the more advanced `ParentDocumentRetriever`.

#### **What it is:**

The PDR is a sophisticated technique that balances search precision with contextual richness. The process involves two different text splitters:

1.  **`child_splitter` (`RecursiveCharacterTextSplitter`, chunk_size=400):** This splitter breaks down the source documents into very small, granular chunks. **These small chunks are what get vectorized** and put into the FAISS vector store. Their small size makes them ideal for precise semantic matching against a user's query.
2.  **`parent_splitter` (`RecursiveCharacterTextSplitter`, chunk_size=2000):** This splitter breaks documents into much larger, more contextually complete chunks. These chunks are not vectorized but are stored in a separate document store (`InMemoryStore`).

#### **Why this Strategy Was Chosen:**

This approach solves a fundamental trade-off in RAG systems:
*   **Problem with Small Chunks:** Small chunks are great for finding exact matches but often lack the surrounding context needed for an LLM to generate a high-quality answer. The LLM might only see one isolated paragraph.
*   **Problem with Large Chunks:** Large chunks provide great context but dilute the vector representation, making it harder to match specific user queries. The embedding becomes an "average" of too many concepts.

The **Parent Document Retriever provides the best of both worlds**. The system performs its vector search against the small, precise *child chunks*. When a relevant child chunk is found, the system traces it back to its larger *parent chunk* and retrieves that instead. This retrieved parent chunk is then passed to the LLM, giving it the rich, surrounding context it needs to formulate a comprehensive and accurate answer.

---

## 4. Vectorization and Storage

Once the splitting strategy is defined, the documents are embedded and stored.

*   **Vectorization Model:** `GoogleGenerativeAIEmbeddings` (`models/embedding-001`) is used to convert the text of each *child document* into a 768-dimension numerical vector.
*   **Vectorstore:** `FAISS` is used as the vector database. It stores the embeddings of the child documents and allows for extremely fast similarity searches, enabling the system to find the most relevant child chunks for a given query in milliseconds.
*   **Document Store:** `langchain.storage.InMemoryStore` acts as a simple key-value database. It stores the full text of the *parent documents*, mapping a unique ID to each one. This allows the PDR to quickly fetch the parent content once a child is identified.

---

## 5. Caching for Production-Grade Efficiency

Running the full ingestion pipeline is computationally expensive and, for a static knowledge base, unnecessary to do on every startup.

*   **Implementation:** After the first successful run, the system saves the populated `FAISS` index to a directory (`app/cache/faiss_pdr_index`) and serializes the `InMemoryStore` to a pickle file (`app/cache/pdr_docstore.pkl`).
*   **The Benefit:** On subsequent launches, the `main.py` script first checks for the existence of these cached files. If they are found, it loads them directly into memory, bypassing the entire Load -> Split -> Embed -> Store process. This reduces the application's startup time from minutes to seconds, a crucial feature for development and deployment.