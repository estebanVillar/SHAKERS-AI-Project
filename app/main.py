# app/main.py

import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# LangChain components
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# --- 1. LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
# Ensure the GOOGLE_API_KEY is available
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# --- 2. INITIALIZE THE RAG PIPELINE (on application start) ---
print("Initializing RAG pipeline...")

# Load documents from the knowledge base
loader = DirectoryLoader('./data/knowledge_base/', glob="**/*.md", loader_cls=TextLoader)
documents = loader.load()

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs = text_splitter.split_documents(documents)

# Create embeddings using Google Gemini
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Create the FAISS vector store from the documents
# This is the "indexing" step and will be performed once on startup.
db = FAISS.from_documents(docs, embeddings)

print("RAG pipeline initialized successfully.")

# --- 3. CREATE FLASK APP ---
app = Flask(__name__)

# --- 4. DEFINE API ENDPOINT ---
@app.route('/api/query', methods=['POST'])
def handle_query():
    """
    Handles incoming queries for the RAG system.
    """
    # Get the user's query from the request body
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    user_query = data['query']
    
    # Perform similarity search (Retrieval)
    # This searches the vector store for the most relevant document chunks
    try:
        retrieved_docs = db.similarity_search(user_query, k=2) # Retrieve top 2 relevant docs
        
        # For now, we'll just return the content of the retrieved docs
        # In the next step, we'll feed this to an LLM
        response_data = [
            {
                "content": doc.page_content,
                "source": doc.metadata.get('source', 'Unknown')
            } for doc in retrieved_docs
        ]
        
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 5. RUN THE FLASK APP ---
if __name__ == '__main__':
    # The debug=True flag allows for hot-reloading when you save changes
    app.run(host='0.0.0.0', port=5000, debug=True)