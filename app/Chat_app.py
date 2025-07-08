# app/Chat_app.py
# This file defines the Streamlit user interface for the AI Support Assistant.
# It handles all front-end logic, including rendering the chat, managing session
# state, and communicating with the Flask backend via API calls.

# ==============================================================================
# --- 1. IMPORTS AND INITIAL SETUP ---
# ==============================================================================

import streamlit as st
import requests
import re
from datetime import datetime
from app.metrics_page import display_metrics

# Set the page configuration for the Streamlit app.
# This is the first Streamlit command to run and sets global page settings.
st.set_page_config(
    page_title="Shakers AI Chat",
    page_icon="🤖",
    layout="wide"
)

# ==============================================================================
# --- 2. CUSTOM CSS STYLING ---
# ==============================================================================

# Inject a block of custom CSS to override default Streamlit styles and
# implement the requested custom theme.
st.markdown("""
<style>
/* Main container for the logo in the sidebar */
.logo-container {
    background-color: #C5F555; /* Shakers bright green */
    border-radius: 12px;
    padding: 1rem;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 1rem; /* Space below the logo */
}

/* Ensure the logo itself has a transparent background */
.logo-container img {
    background: transparent;
}

/* --- Button Text Color Fixes --- */

/* For selected/primary buttons in the sidebar navigation */
[data-testid="stSidebarNav"] button[kind="primary"] p,
[data-testid="stSidebarNavButton-active"] p {
    color: #1E1E1E !important; /* Force dark text color on bright background */
}

/* For primary buttons in the main content area */
.stButton > button:not([kind="secondary"]) {
     background-color: #C5F555;
     color: #1E1E1E;
     border: none;
}
.stButton > button:not([kind="secondary"]):hover {
    background-color: #b1da47;
    color: #1E1E1E;
    border: none;
}
.stButton > button:not([kind="secondary"]):active {
    background-color: #a2c63f !important;
    color: #1E1E1E !important;
    border: none !important;
}

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 3. GLOBAL CONSTANTS & SESSION STATE INITIALIZATION ---
# ==============================================================================

# A list of predefined questions to show to the user in a new chat.
INITIAL_SUGGESTIONS = [
    "What is this chatbot capable of?",
    "List the main technologies used in this chatbot.",
    "Explain the project's architecture at a high level."
]

# This function sets up the Streamlit session state.
# Session state is a dictionary that persists variables across reruns for a single user session.
def initialize_session():
    """Initializes all necessary variables in the session state if they don't exist."""
    # Tracks the current page being displayed ('chat' or 'metrics').
    if "current_page" not in st.session_state:
        st.session_state.current_page = "chat"
    
    # A dictionary to store all chat sessions. Key is chat_id, value is session data.
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}
        
    # The ID of the currently active chat. If it's missing, create a new chat.
    if "current_chat_id" not in st.session_state or not st.session_state.current_chat_id:
        new_chat()
        
    # A unique ID for the current user to track their profile on the backend.
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user_{datetime.now().timestamp()}"
        
    # A temporary variable to hold a request from a button click, to be processed on the next rerun.
    if "request_to_process" not in st.session_state:
        st.session_state.request_to_process = None
        
    # A set to keep track of which messages have already had feedback submitted for them.
    if "feedback_submitted_for" not in st.session_state:
        st.session_state.feedback_submitted_for = set()

# ==============================================================================
# --- 4. BACKEND COMMUNICATION & SESSION MANAGEMENT FUNCTIONS ---
# ==============================================================================

def send_feedback(score, user_query, assistant_answer):
    """Sends user feedback to the backend API."""
    try:
        # Make a POST request to the feedback endpoint.
        requests.post(
            "http://127.0.0.1:5000/api/feedback",
            json={
                "user_id": st.session_state.user_id,
                "query": user_query,
                "answer": assistant_answer,
                "score": score
            }
        )
        # Record that feedback was submitted for this answer to hide the buttons.
        st.session_state.feedback_submitted_for.add(assistant_answer)
        st.toast("Thank you for your feedback!", icon="🎉")
    except Exception as e:
        st.error(f"Could not send feedback: {e}")

def new_chat():
    """Creates a new, empty chat session and sets it as the active chat."""
    chat_id = f"chat_{datetime.now().timestamp()}"
    st.session_state.current_chat_id = chat_id
    st.session_state.chat_sessions[chat_id] = {
        "title": "New Chat",
        "messages": [{"role": "assistant", "content": "Hello! Ask me anything about how this chatbot was built, or choose one of the suggestions below."}],
        "recommendations": []
    }
    # Reset the view to the chat page and clear feedback history for the new chat.
    st.session_state.current_page = "chat"
    st.session_state.feedback_submitted_for = set()

def handle_button_click(display_query: str, topic_id: str = None):
    """Stores a query from a button click in session state to be processed on the next app rerun."""
    st.session_state.request_to_process = {
        "display_query": display_query,
        "topic_id": topic_id
    }

# ==============================================================================
# --- 5. MAIN APPLICATION EXECUTION ---
# ==============================================================================

# Call the initialization function at the start of every script run.
initialize_session()

# --- Render the Sidebar UI ---
with st.sidebar:
    # Use st.markdown with a custom class to apply the CSS styling for the logo container.
    st.markdown(
        '<div class="logo-container"><img src="https://www.shakersworks.com/hubfs/shakers_2024/logo.svg" width="150"></div>',
        unsafe_allow_html=True
    )
    st.title("AI Support Assistant")

    # Navigation buttons
    if st.button("➕ New Chat", use_container_width=True):
        new_chat()
        st.rerun() # Rerun the script immediately to reflect the new chat.

    # The 'type' parameter makes the active button primary (bright).
    if st.button("💬 Chat", use_container_width=True, type="primary" if st.session_state.current_page == "chat" else "secondary"):
        st.session_state.current_page = "chat"
        st.rerun()

    if st.button("📊 Metrics", use_container_width=True, type="primary" if st.session_state.current_page == "metrics" else "secondary"):
        st.session_state.current_page = "metrics"
        st.rerun()

    st.markdown("---")
    st.subheader("Chat History")
    # Display buttons for each past chat session, in reverse chronological order.
    for chat_id, session_data in reversed(list(st.session_state.chat_sessions.items())):
        if st.button(session_data['title'], key=f"history_{chat_id}", use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.session_state.current_page = "chat"
            st.rerun()

# --- Conditional Rendering of Main Page Content ---
if st.session_state.current_page == "chat":
    # Get the data for the currently selected chat.
    current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
    st.header(current_chat["title"])

    # Loop through and display all messages in the current chat.
    for i, message in enumerate(current_chat["messages"]):
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            
            # Check if this is the last message AND it's from the assistant.
            is_last_assistant_message = (i == len(current_chat["messages"]) - 1 and message["role"] == "assistant")
            
            # Show feedback buttons only on the last assistant message if feedback hasn't been given yet.
            if is_last_assistant_message and message["content"] not in st.session_state.feedback_submitted_for:
                if i > 0 and current_chat["messages"][i-1]["role"] == "user":
                    user_query_for_feedback = current_chat["messages"][i-1]["content"]
                    # Extract only the core answer, stripping away sources for feedback logging.
                    answer_for_feedback = re.split(r'\n\n\*\*Source', message["content"], flags=re.IGNORECASE)[0].strip()
                    st.markdown("---")
                    feedback_cols = st.columns([1, 1, 8]) # Layout for feedback buttons.
                    with feedback_cols[0]:
                        st.button("👍", key=f"helpful_{i}", on_click=send_feedback, args=(1, user_query_for_feedback, answer_for_feedback), help="This response was helpful")
                    with feedback_cols[1]:
                        st.button("👎", key=f"unhelpful_{i}", on_click=send_feedback, args=(-1, user_query_for_feedback, answer_for_feedback), help="This response was not helpful")

    st.markdown("---")
    
    # --- Conditionally display initial suggestions or recommendations ---
    is_new_chat = (len(current_chat["messages"]) <= 1)
    
    if is_new_chat:
        st.write("Some things you can ask me:")
        cols = st.columns(len(INITIAL_SUGGESTIONS))
        for i, suggestion in enumerate(INITIAL_SUGGESTIONS):
            with cols[i]:
                st.button(suggestion, on_click=handle_button_click, args=(suggestion,), use_container_width=True)
    
    elif current_chat.get("recommendations"): # If recommendations exist for this chat...
        st.write("Here are some other topics you might find interesting:")
        cols = st.columns(len(current_chat["recommendations"]))
        for i, rec in enumerate(current_chat["recommendations"]):
            with cols[i]:
                display_query = f"Please explain more about '{rec['title']}'"
                st.button(
                    rec['title'], 
                    key=f"rec_{rec['topic_id']}_{st.session_state.current_chat_id}",
                    on_click=handle_button_click,
                    args=(display_query, rec['topic_id']),
                    help=rec['explanation'],
                    use_container_width=True
                )

    # --- Process User Input (from text input or button clicks) ---
    request = None # Initialize to None to prevent NameError on reruns.

    if st.session_state.request_to_process:
        # A button was clicked. Use the request stored in session state.
        request = st.session_state.request_to_process
        st.session_state.request_to_process = None # Clear it after processing.
    else:
        # No button was clicked, check for text input from the user.
        user_input = st.chat_input("Ask about the RAG pipeline, recommendations, evaluation...")
        if user_input:
            request = {"display_query": user_input, "topic_id": None}

    # If a request exists (from either source), process it.
    if request:
        prompt = request["display_query"]
        topic_id_from_button = request.get("topic_id")

        # Append the user's message to the chat history.
        current_chat["messages"].append({"role": "user", "content": prompt})
        # If it's a new chat, set the title to the first user message.
        if current_chat["title"] == "New Chat":
            current_chat["title"] = prompt[:35] + "..." if len(prompt) > 35 else prompt
        
        # Display the user's message immediately.
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display a thinking spinner while waiting for the backend response.
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = "Sorry, an error occurred." # Default error message.
                try:
                    # Determine which API endpoint to call based on the request.
                    if topic_id_from_button:
                        # This request came from a recommendation button click.
                        response = requests.post(
                            "http://127.0.0.1:5000/api/get_document", 
                            json={"topic": topic_id_from_button, "user_id": st.session_state.user_id}
                        )
                    else:
                        # This is a standard query from the text input.
                        response = requests.post(
                            "http://127.0.0.1:5000/api/query",
                            json={
                                "query": prompt,
                                "chat_history": [msg for msg in current_chat["messages"] if msg['role'] in ['user', 'assistant']][:-1],
                                "user_id": st.session_state.user_id
                            }
                        )
                    
                    response.raise_for_status() # Raise an exception for HTTP error codes (4xx or 5xx).
                    data = response.json()
                    answer = data.get("answer", "Failed to get a valid response.")
                    
                    # After getting the answer, fetch new recommendations based on the updated user profile.
                    rec_response = requests.post(
                        "http://127.0.0.1:5000/api/recommendations",
                        json={"user_id": st.session_state.user_id}
                    )
                    if rec_response.status_code == 200:
                         current_chat["recommendations"] = rec_response.json().get("recommendations", [])
                    else:
                        st.warning("Could not fetch new recommendations.")
                        current_chat["recommendations"] = []

                # Handle potential exceptions gracefully.
                except requests.exceptions.ConnectionError:
                    answer = "Error: Could not connect to the backend server. Is `app/main.py` running?"
                    st.error(answer)
                except requests.exceptions.HTTPError as e:
                    answer = f"An API error occurred: {e.response.status_code} - {e.response.text}"
                    st.error(answer)
                except Exception as e:
                    answer = f"An unexpected error occurred: {e}"
                    st.error(answer)
        
        # Append the final assistant answer to the chat history.
        current_chat["messages"].append({"role": "assistant", "content": answer})
        st.rerun() # Rerun the script to display the new message and recommendations.

# If the user selected the 'Metrics' page, call its display function.
elif st.session_state.current_page == "metrics":
    display_metrics()
