# app/ui.py (Updated)

import streamlit as st
import requests

# --- CONFIGURATION ---
# NEW: Add the URL for the recommendation endpoint
QUERY_API_URL = "http://127.0.0.1:5000/api/query"
RECOMMENDATION_API_URL = "http://127.0.0.1:5000/api/recommendations"

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Shakers Support AI",
    page_icon="🤖"
)

st.title("🤖 Shakers AI Support")
st.caption("Your intelligent assistant for the Shakers platform.")

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
# NEW: Initialize session state for recommendations
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

# --- CHAT HISTORY DISPLAY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            sources_str = ", ".join([s.replace('data/knowledge_base/', '').replace('data\\knowledge_base\\', '') for s in message["sources"]])
            st.info(f"Sources: {sources_str}")

# --- USER INPUT AND API CALLS ---
if prompt := st.chat_input("Ask me anything about Shakers..."):
    # 1. Add user message and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call the RAG Query API
    try:
        api_response = requests.post(QUERY_API_URL, json={"query": prompt})
        api_response.raise_for_status()
        response_data = api_response.json()
        answer = response_data.get("answer", "Sorry, something went wrong.")
        sources = response_data.get("sources", [])
    except requests.exceptions.RequestException as e:
        answer = f"Error: Could not connect to the backend service. Please ensure it's running. Details: {e}"
        sources = []
    
    # 3. Add assistant response and display it
    assistant_message = {"role": "assistant", "content": answer, "sources": sources}
    st.session_state.messages.append(assistant_message)
    with st.chat_message("assistant"):
        st.markdown(answer)
        if sources:
            sources_str = ", ".join([s.replace('data/knowledge_base/', '').replace('data\\knowledge_base\\', '') for s in sources])
            st.info(f"Sources: {sources_str}")
            
    # --- NEW: 4. FETCH AND UPDATE RECOMMENDATIONS ---
    # We build the query history from the user messages in the session state
    query_history = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
    
    try:
        rec_response = requests.post(RECOMMENDATION_API_URL, json={"query_history": query_history})
        rec_response.raise_for_status()
        rec_data = rec_response.json()
        # Store the recommendations in the session state
        st.session_state.recommendations = rec_data.get("recommendations", [])
    except requests.exceptions.RequestException as e:
        # Don't show an error for recommendations, just log it or fail silently
        print(f"Could not fetch recommendations: {e}")
        st.session_state.recommendations = []

# --- NEW: 5. DISPLAY RECOMMENDATIONS IN THE SIDEBAR ---
if st.session_state.recommendations:
    with st.sidebar:
        st.subheader("Recommended for you")
        for rec in st.session_state.recommendations:
            # Clean up the title for display
            clean_title = rec['title'].replace('.md', '').replace('_', ' ').title()
            with st.expander(clean_title):
                st.markdown(rec['explanation'])