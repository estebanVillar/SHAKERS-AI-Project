# app/1_Chat.py

import streamlit as st
import requests
import time

# --- CONFIGURACIÓN ---
QUERY_API_URL = "http://127.0.0.1:5000/api/query"
RECOMMENDATION_API_URL = "http://127.0.0.1:5000/api/recommendations"

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Shakers AI Chat",
    page_icon="🤖",
    layout="wide"  # CAMBIO: Usar layout ancho para ocupar toda la pantalla
)

# --- CSS PARA EL DISEÑO DE PANTALLA COMPLETA ---
st.markdown("""
<style>
    /* 1. Eliminar el padding extra que Streamlit añade al layout "wide" */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    /* 2. Header de Shakers */
    .chat-header {
        background-color: #D4FF00;
        color: #1A202C;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 600;
        font-size: 1.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    /* 3. Estilo de las burbujas de chat (sin cambios) */
    [data-testid="stChatMessage"]:has(span[data-testid="chat-avatar-assistant"]) .st-emotion-cache-1c7y2kd {
        background-color: #f0f2f6;
    }
    
    [data-testid="stChatMessage"]:has(span[data-testid="chat-avatar-user"]) .st-emotion-cache-1c7y2kd {
        background-color: #1A202C;
        color: #FFFFFF;
    }
    
    /* 4. Estilo de la barra lateral */
    [data-testid="stSidebar"] {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# --- HEADER ---
st.markdown('<div class="chat-header"><span>💬</span> Tus chats</div>', unsafe_allow_html=True)


# --- LÓGICA DEL CHAT (sin cambios) ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "¿En qué puedo ayudarte hoy?"}]
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            sources_str = ", ".join([s.split('/')[-1].split('\\')[-1] for s in message["sources"]])
            st.caption(f"Fuentes: {sources_str}")

def process_chat(prompt: str):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Pensando..."):
            try:
                # El historial se envía para permitir conversaciones con contexto
                api_response = requests.post(QUERY_API_URL, json={"query": prompt, "chat_history": st.session_state.messages})
                response_data = api_response.json()
                answer = response_data.get("answer", "Lo siento, algo salió mal.")
                sources = response_data.get("sources", [])
            except requests.exceptions.RequestException:
                answer, sources = "Error: No se pudo conectar con el servidor.", []
        st.markdown(answer)
        if sources:
            sources_str = ", ".join([s.split('/')[-1].split('\\')[-1] for s in sources])
            st.caption(f"Fuentes: {sources_str}")
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    query_history = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
    try:
        rec_response = requests.post(RECOMMENDATION_API_URL, json={"query_history": query_history})
        st.session_state.recommendations = rec_response.json().get("recommendations", [])
    except Exception:
        st.session_state.recommendations = []

if prompt := st.chat_input("Escribe tu mensaje..."):
    process_chat(prompt)

if st.session_state.recommendations:
    with st.sidebar:
        st.subheader("Recomendado para ti")
        for rec in st.session_state.recommendations:
            clean_title = rec['title'].replace('.md', '').replace('_', ' ').title()
            with st.expander(clean_title):
                st.markdown(rec['explanation'])