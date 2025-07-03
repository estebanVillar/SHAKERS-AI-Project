# app/main.py

import os
import re
import json
import time
import pickle
import threading
import numpy as np
from scipy.spatial.distance import cosine
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# --- LangChain & GenAI Imports ---
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.storage import InMemoryStore
from langchain.retrievers import ParentDocumentRetriever

# ==============================================================================
# --- 1. INITIAL SETUP & CONFIGURATION ---
# ==============================================================================
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please add it.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
VECTORSTORE_PATH = os.path.join(CACHE_DIR, 'faiss_pdr_index')
DOCSTORE_PATH = os.path.join(CACHE_DIR, 'pdr_docstore.pkl')
USER_PROFILES_PATH = os.path.join(BASE_DIR, 'data', 'evaluation', 'user_profiles.json')
QUERY_LOGS_PATH = os.path.join(PROJECT_ROOT, 'query_logs.jsonl')
KNOWLEDGE_BASE_PATH = os.path.join(PROJECT_ROOT, 'data\knowledge_base')

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(USER_PROFILES_PATH), exist_ok=True)
file_lock = threading.Lock()

# ==============================================================================
# --- 2. DATA LOADING AND RAG PIPELINE INITIALIZATION ---
# ==============================================================================
print("Initializing RAG pipeline with Parent Document Retriever...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
llm = GoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2)

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
doc_embeddings_cache = {}

if os.path.exists(VECTORSTORE_PATH) and os.path.exists(DOCSTORE_PATH):
    print("Loading retriever components from cache...")
    vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    with open(DOCSTORE_PATH, 'rb') as f:
        store = pickle.load(f)
    print("✅ Cached retriever loaded successfully.")
else:
    print("No cache found. Performing full one-time initialization...")
    loader = DirectoryLoader(
        KNOWLEDGE_BASE_PATH, glob="**/*.md", loader_cls=TextLoader,
        show_progress=True, use_multithreading=True, loader_kwargs={"encoding": "utf-8"}
    )
    all_docs = loader.load()
    vectorstore = FAISS.from_texts(texts=["_"], embedding=embeddings) 
    store = InMemoryStore()
    retriever_for_setup = ParentDocumentRetriever(
        vectorstore=vectorstore, docstore=store, child_splitter=child_splitter, parent_splitter=parent_splitter
    )
    print(f"Adding {len(all_docs)} documents to the retriever...")
    retriever_for_setup.add_documents(all_docs, ids=None, add_to_docstore=True)
    print("Saving retriever components to cache...")
    vectorstore.save_local(VECTORSTORE_PATH)
    with open(DOCSTORE_PATH, 'wb') as f: pickle.dump(store, f)
    print("✅ Initialization complete and retriever cached successfully.")

retriever = ParentDocumentRetriever(vectorstore=vectorstore, docstore=store, child_splitter=child_splitter)

print("Pre-computing embeddings for all documents for recommendations...")
all_full_docs = list(store.mget(list(store.yield_keys())))
for doc in all_full_docs:
    relative_path = os.path.relpath(doc.metadata['source'], KNOWLEDGE_BASE_PATH)
    path_parts = relative_path.split(os.sep)
    cleaned_parts = [re.sub(r'^\d+-', '', part).replace('.md', '') for part in path_parts]
    doc.metadata['topic'] = "/".join(cleaned_parts)
    doc_embedding = embeddings.embed_query(doc.page_content)
    doc_embeddings_cache[doc.metadata['topic']] = { "content": doc.page_content, "embedding": doc_embedding }
print(f"✅ Cached {len(doc_embeddings_cache)} document embeddings.")

# --- ADVANCED CONVERSATIONAL CHAIN SETUP ---
recontextualization_prompt = ChatPromptTemplate.from_messages([
    ("system", "Given a chat history and a follow-up question, rephrase the follow-up question to be a standalone question that captures all relevant context."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
])
history_aware_retriever = create_history_aware_retriever(llm, retriever, recontextualization_prompt)

system_template = """You are an expert AI assistant documenting the chatbot you are part of. Your task is to answer user questions about your own architecture and functionality based ONLY on the provided context.
The context below contains document chunks, each with a 'topic' in its metadata.
Follow these rules strictly:
1. Synthesize the information from the context to provide a clear, concise answer.
2. Do NOT add any information that is not in the context.
3. At the end of sentences or paragraphs, you MUST cite the topics of the sources you used in the format `[topic/name]`. For example, a fact from a source with topic 'api-reference/rag-query-service' should be cited as `[api-reference/rag-query-service]`.
4. If the answer is not found in the context, you MUST respond with: "I'm sorry, I don't have enough information to answer that question based on the provided documents."

Context:
{context}

Question:
{input}

Answer (with citations):"""
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}")
])
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
print("✅ Advanced Conversational RAG pipeline ready.")


# ==============================================================================
# --- 4. HELPER FUNCTIONS & FLASK APP ---
# ==============================================================================
def load_user_profiles():
    with file_lock:
        if not os.path.exists(USER_PROFILES_PATH): return {}
        try:
            with open(USER_PROFILES_PATH, 'r') as f: return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError): return {}

def save_user_profiles(profiles):
    with file_lock:
        with open(USER_PROFILES_PATH, 'w') as f: json.dump(profiles, f, indent=4)

def log_query(log_entry):
    with file_lock:
        with open(QUERY_LOGS_PATH, "a") as f: f.write(json.dumps(log_entry) + "\n")

app = Flask(__name__)

@app.route('/api/get_document', methods=['POST'])
def get_document_by_topic():
    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({"error": "Missing 'topic' in request body"}), 400
    
    topic_to_find = data['topic']
    document_data = doc_embeddings_cache.get(topic_to_find)

    if not document_data:
        return jsonify({"answer": f"Sorry, I could not find a document for the topic: {topic_to_find}."})

    prompt = ChatPromptTemplate.from_template(
        "You are an AI assistant. A user has requested information about '{topic}'. Below is the full text of the relevant document. "
        "Provide a comprehensive summary of this document, capturing the key points clearly.\n\n"
        "Document Content:\n---\n{context}\n---\n\nSummary:"
    )
    summarization_chain = prompt | llm | StrOutputParser()
    answer = summarization_chain.invoke({"topic": topic_to_find, "context": document_data['content']})
    
    log_query({
        "timestamp": datetime.utcnow().isoformat(), "user_id": data.get("user_id", "unknown"), 
        "query": f"Direct request for topic: {topic_to_find}", "answer": answer, 
        "sources": [topic_to_find], "latency_ms": 0
    })
    return jsonify({"answer": answer, "sources": [topic_to_find]})

@app.route('/api/query', methods=['POST'])
def handle_query():
    start_time = time.time()
    data = request.get_json()
    if not data or 'query' not in data or 'user_id' not in data:
        return jsonify({"error": "Request must include 'query', 'user_id'"}), 400
    
    user_query = data['query']
    user_id = data['user_id']
    chat_history_json = data.get('chat_history', [])
    chat_history_messages = [HumanMessage(content=msg['content']) if msg['role'] == 'user' else AIMessage(content=msg['content']) for msg in chat_history_json]

    try:
        print(f"ℹ️ Using unified RAG chain for query: '{user_query}'")
        result = rag_chain.invoke({"input": user_query, "chat_history": chat_history_messages})
        generated_answer = result.get('answer', "An unexpected error occurred.")
        source_docs = result.get('context', [])
        source_topics = sorted(list(set(doc.metadata.get('topic', 'Unknown') for doc in source_docs)))

        user_profiles = load_user_profiles()
        if user_id not in user_profiles:
            user_profiles[user_id] = {"query_history": [], "inferred_interests": [], "profile_vector": None}
        user_profiles[user_id]["query_history"].append({"query": user_query, "timestamp": datetime.utcnow().isoformat()})
        if source_topics:
            for topic in source_topics:
                if topic not in user_profiles[user_id]["inferred_interests"]:
                    user_profiles[user_id]["inferred_interests"].append(topic)
        
        query_vector = embeddings.embed_query(user_query)
        old_vector = user_profiles[user_id].get("profile_vector")
        new_vector = np.mean([np.array(old_vector), np.array(query_vector)], axis=0).tolist() if old_vector else query_vector
        user_profiles[user_id]["profile_vector"] = new_vector
        save_user_profiles(user_profiles)
        
        latency = (time.time() - start_time) * 1000
        log_query({"timestamp": datetime.utcnow().isoformat(), "user_id": user_id, "query": user_query, "answer": generated_answer, "sources": source_topics, "latency_ms": round(latency)})
        
        return jsonify({"answer": generated_answer, "sources": source_topics})
    except Exception as e:
        import traceback
        print(f"Error handling query: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/api/recommendations', methods=['POST'])
def handle_recommendations():
    data = request.get_json()
    if not data or 'user_id' not in data: return jsonify({"error": "Missing 'user_id'"}), 400
    user_id = data['user_id']
    user_profiles = load_user_profiles()
    user_profile = user_profiles.get(user_id)
    if not user_profile or not user_profile.get("profile_vector"):
        return jsonify({"recommendations": []})

    profile_vector = np.array(user_profile["profile_vector"])
    scores = []
    for topic, data in doc_embeddings_cache.items():
        similarity = 1 - cosine(profile_vector, np.array(data["embedding"]))
        scores.append({"topic": topic, "score": similarity})
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    consulted_topics = set(user_profile.get("inferred_interests", []))
    recommendations = []
    seen_topics = set()
    
    for item in scores:
        if len(recommendations) >= 3: break
        topic = item['topic']
        if topic not in seen_topics:
            is_consulted = topic in consulted_topics
            explanation = ""
            if item['score'] > 0.45 and not is_consulted:
                explanation = f"Highly relevant to your interests and you haven't seen it yet."
            elif item['score'] > 0.45 and is_consulted:
                explanation = f"You've touched on this; a review might offer deeper insights."
            elif item['score'] > 0.35 and not is_consulted:
                 explanation = f"To broaden your knowledge, you might find this interesting."
            if explanation:
                recommendations.append({"title": topic, "explanation": explanation})
                seen_topics.add(topic)

    if len(recommendations) < 3:
        for item in scores:
            if len(recommendations) >= 3: break
            if item['topic'] not in seen_topics:
                 recommendations.append({"title": item['topic'], "explanation": f"This could be a related topic to explore."})
                 seen_topics.add(item['topic'])

    return jsonify({"recommendations": recommendations})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)