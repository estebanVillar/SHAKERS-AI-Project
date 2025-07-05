# Implementation: Ingestion and Indexing

## 1. Overview
This document details the one-time pipeline that processes the raw markdown files from the `knowledge_base/` directory into a high-performance, searchable index. This process, which runs when `main.py` is first launched, follows a **Load -> Split -> Embed -> Store** pattern and is foundational to the chatbot's ability to find information.

---

## 2. The Four Key Steps of the Pipeline

### 2.1. Step 1: Loading Documents (`DirectoryLoader`)
The process begins in `main.py` by initializing a `langchain_community.document_loaders.DirectoryLoader`. This component is configured with the following key parameters:
*   `path=KNOWLEDGE_BASE_PATH`: It points to the root of our documentation.
*   `glob="**/*.md"`: It's instructed to recursively find all files ending in `.md` in any subdirectory.
*   `loader_cls=TextLoader`: It specifies that each found file should be read as plain text.
*   `use_multithreading=True`: This speeds up the I/O process of reading multiple files from disk.
The output of `loader.load()` is a list of LangChain `Document` objects, where each object contains the page content and metadata (like the source file path).

### 2.2. Step 2: The Splitting Strategy (`ParentDocumentRetriever`)
To prepare the documents for efficient retrieval, we use the `ParentDocumentRetriever`. This is not just a splitter, but a complete retrieval strategy that uses two distinct text splitters internally.
*   **`child_splitter` (`RecursiveCharacterTextSplitter`, chunk_size=400, chunk_overlap=50):** This splitter breaks the loaded documents into very small, semantically precise chunks. A small chunk size is ideal for vector search, as the resulting embedding is very focused. **These small child chunks are what get embedded.**
*   **`parent_splitter` (`RecursiveCharacterTextSplitter`, chunk_size=2000, chunk_overlap=200):** This splitter breaks the documents into larger, more contextually complete chunks. These chunks are not embedded but are stored for the final answer generation phase.

### 2.3. Step 3: Vectorization and Storage
*   **Vectorization Model:** The `GoogleGenerativeAIEmbeddings` class, configured to use the `models/embedding-001` model, is used to convert the `page_content` of each **child chunk** into a 768-dimension numerical vector.
*   **Vector Store (`FAISS`):** All of the child chunk vectors are then indexed into a `FAISS` vector store. FAISS creates a highly optimized data structure that allows for lightning-fast similarity searches.
*   **Document Store (`InMemoryStore`):** The larger **parent chunks** are stored in a simple key-value store called `InMemoryStore`, which maps a unique ID to the full text of each parent chunk.

### 2.4. Step 4: Caching for Production Efficiency
Running the full ingestion pipeline is computationally expensive and unnecessary to do on every application startup. To solve this, the system implements a robust caching mechanism in `main.py`:
*   **The Check:** The script first checks if `VECTORSTORE_PATH` and `DOCSTORE_PATH` exist in the `app/cache/` directory.
*   **On First Run (No Cache):** The full Load -> Split -> Embed -> Store process is executed. Upon completion, the script saves the results:
    *   `vectorstore.save_local(VECTORSTORE_PATH)`: Serializes the FAISS index to disk.
    *   `pickle.dump(store, f)`: Saves the `InMemoryStore` containing the parent documents to a pickle file.
*   **On Subsequent Runs (Cache Found):** If the cache files exist, the script bypasses the entire ingestion pipeline. It loads the FAISS index and the document store directly into memory, reducing application startup time from minutes to mere seconds.

---

## 3. Design Rationale: "Why This Complex Process?"
This ingestion strategy was deliberately chosen to create a RAG system that is both **precise** and **contextually aware**.
*   **Precision in Search:** Searching against small child chunks allows the system to find the exact paragraph that best matches a user's specific query.
*   **Context in Generation:** Providing the LLM with the larger parent chunk ensures it has enough surrounding information to understand the full context and formulate a high-quality, comprehensive answer.

*To see how this retriever is used in a live query, refer to **`04_03-Implementation-Conversational-Chain.md`*.