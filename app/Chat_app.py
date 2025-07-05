# app/Chat_app.py

import streamlit as st
import requests
import re
from datetime import datetime
from metrics_page import display_metrics

# --- Page and Session State Configuration ---
st.set_page_config(page_title="Shakers AI Chat", page_icon="🤖", layout="wide")

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
        "messages": [{"role": "assistant", "content": "Hello! Ask me anything about how this chatbot was built."}],
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
    for chat_id, session_data in reversed(st.session_state.chat_sessions.items()):
        if st.button(session_data['title'], key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.session_state.current_page = "chat"
            st.rerun()

# --- Main Chat Interface ---
if st.session_state.current_page == "chat":
    current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
    st.header(current_chat["title"])

    for i, message in enumerate(current_chat["messages"]):
        with st.chat_message(message["role"]):
            # SIMPLIFICATION: Directly render the markdown content.
            # The backend now formats the "Sources:" list, so no special parsing is needed.
            st.markdown(message["content"], unsafe_allow_html=True)

            is_last_assistant_message = (i == len(current_chat["messages"]) - 1 and message["role"] == "assistant")
            if is_last_assistant_message and message["content"] not in st.session_state.feedback_submitted_for:
                if i > 0 and current_chat["messages"][i-1]["role"] == "user":
                    user_query_for_feedback = current_chat["messages"][i-1]["content"]
                    # Log only the main answer part for feedback
                    answer_for_feedback = re.split(r'Sources:', message["content"], flags=re.IGNORECASE)[0].strip()

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

    if current_chat.get("recommendations"):
        st.markdown("---")
        st.write("Here are some topics you might find interesting:")
        cols = st.columns(len(current_chat["recommendations"]))
        for i, rec in enumerate(current_chat["recommendations"]):
            with cols[i]:
                st.button(
                    rec['title'],
                    key=f"rec_{rec['title']}_{st.session_state.current_chat_id}",
                    on_click=set_new_query,
                    args=(f"Tell me about {rec['title']}",),
                    help=rec['explanation'],
                    use_container_width=True
                )

    prompt = st.session_state.new_query or st.chat_input("Ask about the RAG pipeline, recommendations, evaluation...")
    if st.session_state.new_query:
        st.session_state.new_query = None # Clear the prompt after using it

    if prompt:
        current_chat["messages"].append({"role": "user", "content": prompt})
        if current_chat["title"] == "New Chat":
            current_chat["title"] = prompt[:35] + "..." if len(prompt) > 35 else prompt
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = "Sorry, an error occurred."
                try:
                    direct_hit_match = re.search(r"Tell me about\s+(.+)", prompt, re.IGNORECASE)
                    if direct_hit_match:
                        topic = direct_hit_match.group(1).strip()
                        response = requests.post(
                            "http://127.0.0.1:5000/api/get_document", 
                            json={"topic": topic, "user_id": st.session_state.user_id}
                        ).json()
                        answer = response.get("answer", "Could not retrieve document.")
                    else:
                        response = requests.post(
                            "http://127.0.0.1:5000/api/query",
                            json={
                                "query": prompt,
                                "chat_history": [msg for msg in current_chat["messages"] if msg['role'] in ['user', 'assistant']][:-1],
                                "user_id": st.session_state.user_id
                            }
                        ).json()
                        answer = response.get("answer", "Failed to get a response from the query endpoint.")
                    
                    # Update recommendations after getting an answer
                    rec_response = requests.post(
                        "http://127.0.0.1:5000/api/recommendations",
                        json={"user_id": st.session_state.user_id}
                    ).json()
                    current_chat["recommendations"] = rec_response.get("recommendations", [])

                except requests.exceptions.ConnectionError:
                    answer = "Error: Could not connect to the backend server. Is `app/main.py` running?"
                    st.error(answer)
                except Exception as e:
                    answer = f"An unexpected error occurred: {e}"
                    st.error(answer)
        
        current_chat["messages"].append({"role": "assistant", "content": answer})
        st.rerun()

# --- Metrics Dashboard ---
elif st.session_state.current_page == "metrics":
    display_metrics()