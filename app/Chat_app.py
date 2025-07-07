# app/Chat_app.py

import streamlit as st
import requests
import re
from datetime import datetime
# --- FIX: Use an absolute import from the 'app' package ---
from app.metrics_page import display_metrics

# --- Page and Session State Configuration ---
st.set_page_config(page_title="Shakers AI Chat", page_icon="🤖", layout="wide")

INITIAL_SUGGESTIONS = [
    "What is this chatbot capable of?",
    "List the main technologies used in this chatbot.",
    "Explain the project's architecture at a high level."
]

def initialize_session():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "chat"
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}
    if "current_chat_id" not in st.session_state or not st.session_state.current_chat_id:
        new_chat()
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user_{datetime.now().timestamp()}"
    if "new_query" not in st.session_state:
        st.session_state.new_query = None
    if "feedback_submitted_for" not in st.session_state:
        st.session_state.feedback_submitted_for = set()

def send_feedback(score, user_query, assistant_answer):
    try:
        requests.post(
            "http://127.0.0.1:5000/api/feedback",
            json={
                "user_id": st.session_state.user_id,
                "query": user_query,
                "answer": assistant_answer,
                "score": score
            }
        )
        st.session_state.feedback_submitted_for.add(assistant_answer)
        st.toast("Thank you for your feedback!", icon="🎉")
    except Exception as e:
        st.error(f"Could not send feedback: {e}")

def new_chat():
    chat_id = f"chat_{datetime.now().timestamp()}"
    st.session_state.current_chat_id = chat_id
    st.session_state.chat_sessions[chat_id] = {
        "title": "New Chat",
        "messages": [{"role": "assistant", "content": "Hello! Ask me anything about how this chatbot was built, or choose one of the suggestions below."}],
        "recommendations": []
    }
    st.session_state.current_page = "chat"
    st.session_state.feedback_submitted_for = set()

def set_new_query(query: str):
    st.session_state.new_query = query

initialize_session()

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://uploads-ssl.webflow.com/645c055c5e638d394b3b3e0e/645c05d76214150538cc8f01_Shakers%20Logo.svg", width=150)
    st.title("AI Support Assistant")

    if st.button("➕ New Chat", use_container_width=True):
        new_chat()
        st.rerun()

    if st.button("💬 Chat", use_container_width=True, type="primary" if st.session_state.current_page == "chat" else "secondary"):
        st.session_state.current_page = "chat"
        st.rerun()

    if st.button("📊 Metrics", use_container_width=True, type="primary" if st.session_state.current_page == "metrics" else "secondary"):
        st.session_state.current_page = "metrics"
        st.rerun()

    st.markdown("---")
    st.subheader("Chat History")
    for chat_id, session_data in reversed(list(st.session_state.chat_sessions.items())):
        if st.button(session_data['title'], key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.session_state.current_page = "chat"
            st.rerun()

# --- Main Chat Interface ---
if st.session_state.current_page == "chat":
    current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
    st.header(current_chat["title"])

    # Display chat messages
    for i, message in enumerate(current_chat["messages"]):
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

            is_last_assistant_message = (i == len(current_chat["messages"]) - 1 and message["role"] == "assistant")
            if is_last_assistant_message and message["content"] not in st.session_state.feedback_submitted_for:
                if i > 0 and current_chat["messages"][i-1]["role"] == "user":
                    user_query_for_feedback = current_chat["messages"][i-1]["content"]
                    answer_for_feedback = re.split(r'\n\n\*\*Source', message["content"], flags=re.IGNORECASE)[0].strip()

                    st.markdown("---")
                    feedback_cols = st.columns([1, 1, 8])
                    with feedback_cols[0]:
                        st.button("👍", key=f"helpful_{i}", on_click=send_feedback, 
                                  args=(1, user_query_for_feedback, answer_for_feedback),
                                  help="This response was helpful")
                    with feedback_cols[1]:
                        st.button("👎", key=f"unhelpful_{i}", on_click=send_feedback,
                                  args=(-1, user_query_for_feedback, answer_for_feedback),
                                  help="This response was not helpful")

    # --- UNIFIED SUGGESTION / RECOMMENDATION AREA ---
    st.markdown("---")
    is_new_chat = (len(current_chat["messages"]) <= 1)
    
    if is_new_chat:
        st.write("Some things you can ask me:")
        cols = st.columns(len(INITIAL_SUGGESTIONS))
        for i, suggestion in enumerate(INITIAL_SUGGESTIONS):
            with cols[i]:
                st.button(suggestion, on_click=set_new_query, args=(suggestion,), use_container_width=True)
    
    elif current_chat.get("recommendations"):
        st.write("Here are some other topics you might find interesting:")
        cols = st.columns(len(current_chat["recommendations"]))
        for i, rec in enumerate(current_chat["recommendations"]):
            with cols[i]:
                # --- FIX: Generate a more natural query on click ---
                st.button(
                    rec['title'], 
                    key=f"rec_{rec['topic_id']}_{st.session_state.current_chat_id}",
                    on_click=set_new_query,
                    args=(f"Please explain more about '{rec['title']}'",),
                    help=rec['explanation'],
                    use_container_width=True
                )

    # --- Chat Input Logic ---
    prompt = st.session_state.new_query or st.chat_input("Ask about the RAG pipeline, recommendations, evaluation...")
    if st.session_state.new_query:
        st.session_state.new_query = None

    if prompt:
        current_chat["messages"].append({"role": "user", "content": prompt})
        if current_chat["title"] == "New Chat":
            current_chat["title"] = prompt[:35] + "..." if len(prompt) > 35 else prompt
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = "Sorry, an error occurred."
                try:
                    # Check for direct document requests (e.g. from evaluation script)
                    direct_hit_match = re.search(r"Tell me about\s+([\w\d_-]+)", prompt, re.IGNORECASE)
                    if direct_hit_match:
                        topic = direct_hit_match.group(1).strip()
                        response = requests.post(
                            "http://127.0.0.1:5000/api/get_document", 
                            json={"topic": topic, "user_id": st.session_state.user_id}
                        )
                    else:
                        response = requests.post(
                            "http://127.0.0.1:5000/api/query",
                            json={
                                "query": prompt,
                                "chat_history": [msg for msg in current_chat["messages"] if msg['role'] in ['user', 'assistant']][:-1],
                                "user_id": st.session_state.user_id
                            }
                        )
                    
                    response.raise_for_status()
                    data = response.json()
                    answer = data.get("answer", "Failed to get a valid response.")
                    
                    rec_response = requests.post(
                        "http://127.0.0.1:5000/api/recommendations",
                        json={"user_id": st.session_state.user_id}
                    )
                    if rec_response.status_code == 200:
                         current_chat["recommendations"] = rec_response.json().get("recommendations", [])
                    else:
                        st.warning("Could not fetch new recommendations.")
                        current_chat["recommendations"] = []

                except requests.exceptions.ConnectionError:
                    answer = "Error: Could not connect to the backend server. Is `app/main.py` running?"
                    st.error(answer)
                except requests.exceptions.HTTPError as e:
                    answer = f"An API error occurred: {e.response.status_code} - {e.response.text}"
                    st.error(answer)
                except Exception as e:
                    answer = f"An unexpected error occurred: {e}"
                    st.error(answer)
        
        current_chat["messages"].append({"role": "assistant", "content": answer})
        st.rerun()

elif st.session_state.current_page == "metrics":
    display_metrics()