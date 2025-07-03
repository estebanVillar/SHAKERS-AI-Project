# app/metrics_page.py
import streamlit as st
import pandas as pd
import json
import os

def display_metrics():
    """Renders the content of the metrics dashboard."""
    st.markdown('<div class="chat-header"><span>📊</span> Metrics Dashboard</div>', unsafe_allow_html=True)

    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "query_logs.jsonl")
    log_data = []
    try:
        with open(log_file_path, 'r') as f:
            log_data = [json.loads(line) for line in f]
    except FileNotFoundError:
        st.warning("Log file not found. Please interact with the chat to generate data.")
        return

    if not log_data:
        st.info("No queries have been logged yet.")
        return

    df = pd.DataFrame(log_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    st.subheader("Core Metrics")
    cols = st.columns(3)
    cols[0].metric("Total Queries", len(df))
    cols[1].metric("Avg. Latency (ms)", f"{df['latency_ms'].mean():.0f}")
    cols[2].metric("Unique Sources", df['sources'].explode().nunique())

    st.subheader("Performance Over Time")
    st.line_chart(df.rename(columns={'latency_ms': 'Latency (ms)'}).set_index('timestamp')['Latency (ms)'])

    st.subheader("Recent Queries Log")
    st.dataframe(df[['timestamp', 'query', 'latency_ms']].tail(10))