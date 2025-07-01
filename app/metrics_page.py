# app/metrics_page.py
import streamlit as st
import pandas as pd
import json
import os

def display_metrics():
    """Función para renderizar el contenido del dashboard de métricas."""
    st.markdown('<div class="chat-header"><span>📊</span> Dashboard de Métricas</div>', unsafe_allow_html=True)

    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "query_logs.jsonl")
    log_data = []
    try:
        with open(log_file_path, 'r') as f:
            log_data = [json.loads(line) for line in f]
    except FileNotFoundError:
        st.warning("No se ha encontrado el archivo de logs. Interactúa con el chat para generar datos.")
        return

    if not log_data:
        st.info("Aún no hay queries registradas.")
        return

    df = pd.DataFrame(log_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    st.subheader("Métricas Principales")
    cols = st.columns(3)
    cols[0].metric("Total Queries", len(df))
    cols[1].metric("Latencia Media (ms)", f"{df['latency_ms'].mean():.0f}")
    cols[2].metric("Fuentes Únicas", df['sources'].explode().nunique())

    st.subheader("Rendimiento a lo Largo del Tiempo")
    st.line_chart(df.rename(columns={'latency_ms': 'Latencia (ms)'}).set_index('timestamp')['Latency (ms)'])

    st.subheader("Logs de Queries Recientes")
    st.dataframe(df[['timestamp', 'query', 'latency_ms']].tail(10))