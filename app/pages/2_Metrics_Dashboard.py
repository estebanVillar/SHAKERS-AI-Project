# app/pages/2_Metrics_Dashboard.py
import streamlit as st
import pandas as pd
import json
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Metrics Dashboard", page_icon="📊", layout="wide")

# --- CSS PARA PANTALLA COMPLETA ---
st.markdown("""
<style>
    /* 1. Eliminar el padding extra de Streamlit */
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
    /* 3. Estilo para las tarjetas de métricas */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="chat-header"><span>📊</span> Dashboard de Métricas</div>', unsafe_allow_html=True)

# --- LÓGICA DEL DASHBOARD (sin cambios) ---
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "query_logs.jsonl")
log_data = []
try:
    with open(log_file_path, 'r') as f:
        log_data = [json.loads(line) for line in f]
except FileNotFoundError:
    st.warning("No se ha encontrado el archivo de logs. Interactúa con el chat para generar datos.")
    st.stop()

if not log_data:
    st.info("Aún no hay queries registradas.")
    st.stop()

df = pd.DataFrame(log_data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

st.subheader("Métricas Principales")
cols = st.columns(3)
cols[0].metric("Total Queries", len(df))
cols[1].metric("Latencia Media (ms)", f"{df['latency_ms'].mean():.0f}")
cols[2].metric("Fuentes Únicas", df['sources'].explode().nunique())

st.subheader("Rendimiento a lo Largo del Tiempo")
st.line_chart(df.rename(columns={'latency_ms': 'Latencia (ms)'}).set_index('timestamp')['Latencia (ms)'])

st.subheader("Logs de Queries Recientes")
st.dataframe(df[['timestamp', 'query', 'latency_ms']].tail(10))