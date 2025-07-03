# app/Chat_app.py

import streamlit as st
import requests
import re # Import the regular expression module
from datetime import datetime
from metrics_page import display_metrics

# --- 1. PAGE & SESSION STATE CONFIGURATION ---
st.set_page_config(page_title="Shakers AI Chat", page_icon="🤖", layout="wide")

def initialize_session():
    """Initializes session state variables."""
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

def new_chat():
    """Creates a new chat session."""
    chat_id = f"chat_{datetime.now().timestamp()}"
    st.session_state.current_chat_id = chat_id
    st.session_state.chat_sessions[chat_id] = {
        "title": "New Chat",
        "messages": [{"role": "assistant", "content": "Hello! Ask me anything about how this chatbot was built."}],
        "recommendations": []
    }
    st.session_state.current_page = "chat"

def set_new_query(query: str):
    """Callback function to set a new query from a button click."""
    st.session_state.new_query = query

initialize_session()

# --- 2. SIDEBAR NAVIGATION ---
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

# --- 3. MAIN CHAT INTERFACE ---
if st.session_state.current_page == "chat":
    current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
    st.header(current_chat["title"])

    for message in current_chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if current_chat.get("recommendations"):
        with st.container():
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

    prompt = None
    if st.session_state.new_query:
        prompt = st.session_state.new_query
        st.session_state.new_query = None

    user_input = st.chat_input("Ask about the RAG pipeline, recommendations, evaluation...")
    if user_input:
        prompt = user_input

    if prompt:
        current_chat["messages"].append({"role": "user", "content": prompt})
        if current_chat["title"] == "New Chat":
            current_chat["title"] = prompt[:35] + "..." if len(prompt) > 35 else prompt
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = "Sorry, an error occurred."
                
                # --- INTELLIGENT ROUTING LOGIC ---
                direct_hit_match = re.search(r"Tell me about\s+(.+)", prompt, re.IGNORECASE)

                try:
                    if direct_hit_match:
                        # ROUTE TO THE DEDICATED ENDPOINT FOR DIRECT REQUESTS
                        topic = direct_hit_match.group(1).strip()
                        response = requests.post(
                            "http://127.0.0.1:5000/api/get_document",
                            json={"topic": topic}
                        ).json()
                        answer = response.get("answer")
                    else:
                        # ROUTE TO THE STANDARD CONVERSATIONAL RAG ENDPOINT
                        response = requests.post(
                            "http://127.0.0.1:5000/api/query", 
                            json={
                                "query": prompt,
                                "chat_history": current_chat["messages"][:-1],
                                "user_id": st.session_state.user_id
                            }
                        ).json()
                        answer = response.get("answer")

                    st.markdown(answer)
                    
                    rec_response = requests.post(
                        "http://127.0.0.1:5000/api/recommendations",
                        json={"user_id": st.session_state.user_id}
                    ).json()
                    current_chat["recommendations"] = rec_response.get("recommendations", [])

                except requests.exceptions.ConnectionError:
                    answer = "Error: Could not connect to the backend server. Is it running?"
                    st.error(answer)
                except Exception as e:
                    answer = f"An unexpected error occurred: {e}"
                    st.error(answer)
        
        current_chat["messages"].append({"role": "assistant", "content": answer})
        st.rerun()

# --- 4. METRICS DASHBOARD ---
elif st.session_state.current_page == "metrics":
    display_metrics()