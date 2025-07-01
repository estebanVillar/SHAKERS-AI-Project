# app/Chat_App.py (o como lo hayas nombrado)

import streamlit as st
import requests
import time
from datetime import datetime
from metrics_page import display_metrics # Importamos la función del dashboard

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Shakers AI Chat",
    page_icon="🤖",
    layout="wide"
)

# --- CSS AVANZADO PARA LA NUEVA UI ---
st.markdown("""
<style>
    /* Ocultar la navegación por defecto de Streamlit (ya que la controlamos nosotros) */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Botones de navegación personalizados en la barra lateral */
    .nav-button {
        width: 100%;
        text-align: left;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        background-color: transparent;
        border: none;
        color: inherit;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        transition: background-color 0.2s;
    }
    .nav-button:hover {
        background-color: #f0f2f6;
    }
    .nav-button-active {
        background-color: #e6eaf1;
    }

    /* Separador en la barra lateral */
    .sidebar-separator {
        margin: 1rem 0;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Botones del historial de chat */
    .history-button {
        /* Estilos similares a nav-button pero más sutil */
        width: 100%;
        text-align: left;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        background-color: transparent;
        border: none;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 0.9rem;
    }
    .history-button:hover {
        background-color: #f0f2f6;
    }
    
    /* Header de Shakers */
    .chat-header {
        background-color: #D4FF00;
        color: #1A202C;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 600;
        font-size: 1.25rem;
    }
    
    /* Burbujas de chat */
    [data-testid="stChatMessage"]:has(span[data-testid="chat-avatar-assistant"]) .st-emotion-cache-1c7y2kd {
        background-color: #f0f2f6;
    }
    [data-testid="stChatMessage"]:has(span[data-testid="chat-avatar-user"]) .st-emotion-cache-1c7y2kd {
        background-color: #1A202C; color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)


# --- LÓGICA DE ESTADO DE SESIÓN ---
def initialize_session():
    """Inicializa el estado de la sesión si es la primera vez."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "chat"
    
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = {}
    
    if "current_chat_id" not in st.session_state:
        # Crear el primer chat al iniciar
        chat_id = f"chat_{datetime.now().timestamp()}"
        st.session_state.current_chat_id = chat_id
        st.session_state.chat_sessions[chat_id] = {
            "title": "Nuevo Chat",
            "messages": [{"role": "assistant", "content": "¿En qué puedo ayudarte hoy?"}]
        }

initialize_session()


# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.subheader("Navegación")
    
    # Botón para nuevo chat, ahora el principal
    if st.button("➕ Nuevo Chat", use_container_width=True):
        chat_id = f"chat_{datetime.now().timestamp()}"
        st.session_state.current_chat_id = chat_id
        st.session_state.chat_sessions[chat_id] = {
            "title": "Nuevo Chat",
            "messages": [{"role": "assistant", "content": "¿En qué puedo ayudarte hoy?"}]
        }
        st.session_state.current_page = "chat"
        st.rerun()

    # Botones de navegación personalizados
    if st.button("💬 Chat", use_container_width=True, type="primary" if st.session_state.current_page == "chat" else "secondary"):
        st.session_state.current_page = "chat"
        # No es necesario un rerun si ya estamos en la página de chat, a menos que se cambie de chat
        # Para simplicidad, lo dejamos, pero se podría optimizar

    if st.button("📊 Métricas", use_container_width=True, type="primary" if st.session_state.current_page == "metrics" else "secondary"):
        st.session_state.current_page = "metrics"
        st.rerun()

    # --- CAMBIO CLAVE: Mostrar el historial SÓLO si hay más de un chat ---
    # Comprobamos si hay chats guardados más allá del inicial.
    if len(st.session_state.chat_sessions) > 1:
        st.markdown("<hr class='sidebar-separator'>", unsafe_allow_html=True)
        st.subheader("Historial")
        
        # Iterar sobre los chats para crear los botones del historial
        # Se muestra del más reciente al más antiguo
        for chat_id in reversed(list(st.session_state.chat_sessions.keys())):
            # No mostrar el chat actualmente activo como un botón de historial para evitar redundancia
            if chat_id == st.session_state.current_chat_id and st.session_state.chat_sessions[chat_id]["title"] == "Nuevo Chat":
                 continue

            chat_title = st.session_state.chat_sessions[chat_id]["title"]
            if st.button(chat_title, key=chat_id, use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.session_state.current_page = "chat"
                st.rerun()

# --- ÁREA PRINCIPAL ---
if st.session_state.current_page == "chat":
    # Lógica para mostrar y procesar el chat activo
    current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
    
    st.markdown(f'<div class="chat-header"><span>💬</span> {current_chat["title"]}</div>', unsafe_allow_html=True)

    for message in current_chat["messages"]:
        avatar = "🤖" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escribe tu mensaje..."):
        # Añadir mensaje de usuario y actualizar título del chat si es el primero
        current_chat["messages"].append({"role": "user", "content": prompt})
        if current_chat["title"] == "Nuevo Chat":
            current_chat["title"] = prompt[:30] + "..." # Usar el primer mensaje como título
        
        # Llamar a la API
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Pensando..."):
                try:
                    response = requests.post(
                        "http://127.0.0.1:5000/api/query", 
                        json={"query": prompt, "chat_history": current_chat["messages"]}
                    ).json()
                    answer = response.get("answer", "Error")
                except Exception:
                    answer = "No se pudo conectar al servidor."
            st.markdown(answer)
        
        current_chat["messages"].append({"role": "assistant", "content": answer})
        st.rerun()

elif st.session_state.current_page == "metrics":
    display_metrics() # Llamamos a la función importada para mostrar el dashboard