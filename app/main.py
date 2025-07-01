# app/main.py (Corrected)

import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# LangChain components
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# --- 1. LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# --- 2. INITIALIZE THE RAG PIPELINE & LOAD DATA ---
print("Initializing RAG pipeline...")
loader = DirectoryLoader('./data/knowledge_base/', glob="**/*.md", loader_cls=TextLoader)
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
docs = text_splitter.split_documents(documents)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
db = FAISS.from_documents(docs, embeddings)
print("RAG pipeline initialized successfully.")

with open('./data/evaluation/user_profiles.json', 'r') as f:
    user_profiles = json.load(f)

# --- 3. INITIALIZE THE LLM AND THE PROMPT TEMPLATE ---
# UPDATED MODEL and FIXED PROMPT
llm = GoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)

prompt_template_str = """
You are a helpful assistant for the Shakers platform.
Your task is to answer user questions based ONLY on the following context.
If the answer is not found in the context, respond with: "I'm sorry, I don't have information on this. Please try asking a different question."
Do not add any information that is not in the context.

Context:
{context}

Question:
{question}

Answer:
"""
# FIXED: Using the recommended .from_template() method
prompt = PromptTemplate.from_template(prompt_template_str)

rag_chain = prompt | llm | StrOutputParser()

# --- 4. CREATE FLASK APP ---
app = Flask(__name__)

# --- 5. DEFINE API ENDPOINTS ---
@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    user_query = data['query']
    
    try:
        retrieved_docs = db.similarity_search(user_query, k=2)
        context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        generated_answer = rag_chain.invoke({"context": context, "question": user_query})

        sources = [doc.metadata.get('source', 'Unknown') for doc in retrieved_docs]
        
        response_data = {
            "answer": generated_answer,
            "sources": list(set(sources))
        }
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Error handling query: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

# --- 6. RECOMMENDATION ENDPOINT ---
def get_topic_from_document(doc_content):
    for line in doc_content.split('\n'):
        if line.startswith('**Topic**: '):
            return line.replace('**Topic**: ', '').strip()
    return None

@app.route('/api/recommendations', methods=['POST'])
def handle_recommendations():
    data = request.get_json()
    if not data or 'query_history' not in data:
        return jsonify({"error": "Missing 'query_history' in request body"}), 400
    
    query_history = data['query_history']
    
    consulted_topics = set()
    for query in query_history:
        retrieved_docs = db.similarity_search(query, k=1)
        for doc in retrieved_docs:
            topic = get_topic_from_document(doc.page_content)
            if topic:
                consulted_topics.add(topic)
                
    all_resources = {
        (
            doc.metadata.get('source').replace('data/knowledge_base/', ''),
            get_topic_from_document(doc.page_content)
        )
        for doc in documents
    }
    
    unconsulted_resources = [
        res for res in all_resources if res[1] and res[1] not in consulted_topics
    ]
    
    recommendations = []
    seen_topics = set()
    for doc_name, topic in unconsulted_resources:
        if topic not in seen_topics:
            recommendations.append({
                "title": doc_name,
                "explanation": f"Since you're exploring the platform, you might find this article on '{topic}' helpful."
            })
            seen_topics.add(topic)
        if len(recommendations) >= 2: # Ensure diversity and limit to 2
            break
            
    return jsonify({"recommendations": recommendations})

# --- 7. RUN THE FLASK APP ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)