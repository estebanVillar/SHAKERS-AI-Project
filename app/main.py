# app/main.py

import time
import threading
import numpy as np
import os
import re
from datetime import datetime
from flask import Flask, request, jsonify, g
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from scipy.spatial.distance import cosine

# --- Local Imports ---
from . import config
from . import utils
from . import rag_pipeline

# ==============================================================================
# --- 1. FLASK APP & BACKGROUND INITIALIZATION ---
# ==============================================================================

app = Flask(__name__)
os.makedirs(os.path.join(config.BASE_DIR, 'data', 'evaluation'), exist_ok=True)

def run_rag_initialization():
    with app.app_context():
        rag_pipeline.initialize_rag_pipeline()

initialization_thread = threading.Thread(target=run_rag_initialization, daemon=True)
initialization_thread.start()

# --- HELPER FUNCTIONS ---
def _format_topic_title(topic_id: str) -> str:
    """Converts a topic ID like '05_02-Implementation-Recommendation-Algorithm' to a readable title."""
    if not topic_id: return "Unknown Topic"
    title_part = re.sub(r'^\d{2}(_\d{2})?-', '', topic_id)
    return title_part.replace('-', ' ').replace('_', ' ').title()

def _update_user_profile(user_id: str, query_text: str, source_topics: list):
    """Loads, updates, and saves a user's profile with new query info."""
    user_profiles = utils.load_user_profiles()
    profile = user_profiles.setdefault(user_id, {"query_history": [], "inferred_interests": [], "profile_vector": None})
    
    profile["query_history"].append({"query": query_text, "timestamp": datetime.utcnow().isoformat()})
    profile["inferred_interests"].extend(t for t in source_topics if t not in profile["inferred_interests"])
    
    # Update profile vector
    query_vector = rag_pipeline.embeddings.embed_query(query_text)
    if profile.get("profile_vector"):
        # Moving average: 80% old vector, 20% new query vector
        new_vector = np.add(np.multiply(profile["profile_vector"], 0.8), np.multiply(query_vector, 0.2)).tolist()
    else:
        new_vector = query_vector
    profile["profile_vector"] = new_vector
    utils.save_user_profiles(user_profiles)
    print(f"Updated profile for user {user_id} based on query: '{query_text[:50]}...'")


# ==============================================================================
# --- 2. API ENDPOINTS ---
# ==============================================================================

@app.before_request
def before_request_func():
    g.start_time = time.time()

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    traceback.print_exc()
    return jsonify({"error": "An internal error occurred.", "details": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def handle_query():
    if not rag_pipeline.get_rag_pipeline_status():
        return jsonify({"error": "RAG pipeline is initializing. Please try again."}), 503

    data = request.get_json()
    if not data or 'query' not in data or 'user_id' not in data:
        return jsonify({"error": "Request must include 'query' and 'user_id'"}), 400

    user_query = data['query']
    user_id = data['user_id']
    chat_history_messages = [
        HumanMessage(content=msg['content']) if msg['role'] == 'user' else AIMessage(content=msg['content'])
        for msg in data.get('chat_history', [])
    ]

    token_callback = utils.TokenUsageCallback()
    result = rag_pipeline.rag_chain.invoke(
        {"input": user_query, "chat_history": chat_history_messages},
        config={"callbacks": [token_callback]}
    )
    generated_answer = result.get('answer', "An unexpected error occurred.")
    failure_signal = "I'm sorry, I don't have enough information"

    source_topics = []
    if failure_signal in generated_answer:
        print("INFO: RAG chain failed. Generating helpful suggestions instead.")
        
        suggestion_prompt_template = (
            "A user asked a question I could not answer. My knowledge is limited to a specific list of technical documents. "
            "Based on the following list of available document topics, generate 3-4 example questions a user could ask that you *would* be able to answer. "
            "**Rule:** Your response MUST ONLY be the list of questions. Each question must start with a hyphen. "
            "**Rule:** Do NOT include any introduction, conclusion, or conversational text like 'Okay, I understand' or 'Here are some questions'. "
            "Just the questions.\n\n"
            "AVAILABLE TOPICS:\n{topics}\n\n"
            "Example Questions:"
        )
        suggestion_prompt = ChatPromptTemplate.from_template(suggestion_prompt_template)
        suggestion_chain = suggestion_prompt | rag_pipeline.llm | StrOutputParser()
        
        all_topics = list(rag_pipeline.doc_embeddings_cache.keys())
        # The same token_callback is used here, so it will correctly sum the tokens from both calls
        suggested_questions_str = suggestion_chain.invoke(
            {"topics": "\n- ".join(all_topics)},
            config={"callbacks": [token_callback]}
        )
        
        intro_message = "That's a great question! Based on the provided documentation, I can't find a specific answer to that. My knowledge is limited to the design and implementation of this chatbot project."
        follow_up_message = "\n\nTo give you an idea of what I can answer, you could ask me something like:"
        generated_answer = f"{intro_message}{follow_up_message}\n{suggested_questions_str}"
        source_topics = ["None"]
    else:
        source_docs = result.get('context', [])
        source_topics = sorted(list(set(doc.metadata.get('topic', 'Unknown') for doc in source_docs)))
        _update_user_profile(user_id, user_query, source_topics)

    latency = (time.time() - g.start_time) * 1000
    input_tokens = token_callback.get_total_prompt_tokens()
    output_tokens = token_callback.get_total_completion_tokens()
    # Calculate cost on the backend
    cost = utils.calculate_cost(input_tokens, output_tokens)

    utils.log_query({
        "timestamp": datetime.utcnow().isoformat(), "user_id": user_id,
        "query": user_query, "answer": generated_answer, "sources": source_topics,
        "latency_ms": round(latency),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost # Log the calculated cost
    })
    return jsonify({"answer": generated_answer, "sources": source_topics})


@app.route('/api/recommendations', methods=['POST'])
def handle_recommendations():
    if not rag_pipeline.get_rag_pipeline_status():
        return jsonify({"error": "RAG pipeline is initializing. Please try again."}), 503

    data = request.get_json()
    if 'user_id' not in data: return jsonify({"error": "Missing 'user_id'"}), 400
    user_id = data['user_id']
    
    user_profiles = utils.load_user_profiles()
    user_profile = user_profiles.get(user_id)
    if not user_profile or not user_profile.get("profile_vector"):
        return jsonify({"recommendations": []})

    profile_vector = np.array(user_profile["profile_vector"])
    consulted_topics = set(user_profile.get("inferred_interests", []))
    
    all_doc_scores = []
    for topic_id, doc_data in rag_pipeline.doc_embeddings_cache.items():
        doc_vector = np.array(doc_data["embedding"])
        similarity = 1 - cosine(profile_vector, doc_vector)
        all_doc_scores.append((similarity, topic_id))

    all_doc_scores.sort(key=lambda x: x[0], reverse=True)

    recommendations = []
    seen_topic_ids = set()
    
    def get_parent_topic(topic_id):
        match = re.match(r"(\d{2}_[a-zA-Z_-]+)", topic_id)
        return match.group(1) if match else topic_id

    seen_parent_topics = set()
    for score, topic_id in all_doc_scores:
        if len(recommendations) >= config.MAX_RECOMMENDATIONS: break
        if topic_id in consulted_topics or topic_id in seen_topic_ids: continue
        parent_topic = get_parent_topic(topic_id)
        if parent_topic not in seen_parent_topics:
            recommendations.append({
                "topic_id": topic_id, "title": _format_topic_title(topic_id),
                "explanation": "Based on your recent interests, you might find this topic helpful."
            })
            seen_topic_ids.add(topic_id)
            seen_parent_topics.add(parent_topic)
            
    if len(recommendations) < config.MAX_RECOMMENDATIONS:
        for score, topic_id in all_doc_scores:
            if len(recommendations) >= config.MAX_RECOMMENDATIONS: break
            if topic_id not in consulted_topics and topic_id not in seen_topic_ids:
                recommendations.append({
                    "topic_id": topic_id, "title": _format_topic_title(topic_id),
                    "explanation": "This related topic might also be of interest to you."
                })
                seen_topic_ids.add(topic_id)
                
    return jsonify({"recommendations": recommendations})


@app.route('/api/feedback', methods=['POST'])
def handle_feedback():
    data = request.get_json()
    utils.log_feedback({
        "timestamp": datetime.utcnow().isoformat(), "user_id": data['user_id'],
        "query": data['query'], "answer": data['answer'], "score": data['score']
    })
    return jsonify({"status": "success", "message": "Feedback received"}), 200


@app.route('/api/get_document', methods=['POST'])
def get_document_by_topic():
    if not rag_pipeline.get_rag_pipeline_status():
        return jsonify({"error": "The RAG pipeline is still initializing. Please try again shortly."}), 503

    data = request.get_json()
    if not data or not all(k in data for k in ['topic', 'user_id']):
        return jsonify({"error": "Missing 'topic' or 'user_id' in request body"}), 400
    
    topic_to_find = data['topic']
    user_id = data['user_id']
    document_data = rag_pipeline.doc_embeddings_cache.get(topic_to_find)

    if not document_data:
        return jsonify({"answer": f"Sorry, I could not find a document for the topic: {topic_to_find}."}), 404

    prompt = ChatPromptTemplate.from_template(
        "You are an AI assistant. A user has requested information about '{topic}'. Below is the full text of the relevant document. "
        "Provide a comprehensive summary of this document, capturing the key points clearly and in a friendly, helpful tone.\n\n"
        "Document Content:\n---\n{context}\n---\n\nSummary:"
    )
    summarization_chain = prompt | rag_pipeline.llm | StrOutputParser()
    
    token_callback = utils.TokenUsageCallback()
    summary = summarization_chain.invoke(
        {"topic": topic_to_find, "context": document_data['content']},
        config={"callbacks": [token_callback]}
    )
    answer = f"{summary}\n\n**Source:** {topic_to_find}"
    
    query_for_profile = f"Tell me about {topic_to_find}"
    _update_user_profile(user_id, query_for_profile, [topic_to_find])
    
    latency = (time.time() - g.start_time) * 1000
    input_tokens = token_callback.get_total_prompt_tokens()
    output_tokens = token_callback.get_total_completion_tokens()
    # Calculate cost on the backend
    cost = utils.calculate_cost(input_tokens, output_tokens)

    utils.log_query({
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "query": query_for_profile,
        "answer": answer,
        "sources": [topic_to_find],
        "latency_ms": round(latency),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost # Log the calculated cost
    })
    
    return jsonify({"answer": answer, "sources": [topic_to_find]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)