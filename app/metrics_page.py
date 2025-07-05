# app/metrics_page.py
import streamlit as st
import pandas as pd
import json
import os

def display_metrics():
    """Renders the content of the metrics dashboard."""
    st.header("📊 Metrics Dashboard")

    # --- QUERY LOGS ---
    st.subheader("Core RAG Metrics")
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "query_logs.jsonl")
    log_data = []
    try:
        with open(log_file_path, 'r') as f:
            log_data = [json.loads(line) for line in f]
    except FileNotFoundError:
        st.warning("Query log file not found. Please interact with the chat to generate data.")

    if not log_data:
        st.info("No queries have been logged yet.")
    else:
        df = pd.DataFrame(log_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        cols = st.columns(3)
        cols[0].metric("Total Queries", len(df))
        cols[1].metric("Avg. Latency (ms)", f"{df['latency_ms'].mean():.0f}")
        cols[2].metric("Unique Sources", df['sources'].explode().nunique())

        st.subheader("Performance Over Time")
        st.line_chart(df.rename(columns={'latency_ms': 'Latency (ms)'}).set_index('timestamp')['Latency (ms)'])

        st.subheader("Recent Queries Log")
        st.dataframe(df[['timestamp', 'query', 'latency_ms']].tail(10), use_container_width=True)

    # --- FEEDBACK METRICS ---
    st.markdown("---")
    st.subheader("User Feedback Metrics")

    feedback_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feedback_logs.jsonl")
    feedback_data = []
    try:
        with open(feedback_file_path, 'r') as f:
            feedback_data = [json.loads(line) for line in f]
    except FileNotFoundError:
        st.warning("No feedback has been submitted yet.")
        return 

    if not feedback_data:
        st.info("No feedback has been logged yet.")
        return

    feedback_df = pd.DataFrame(feedback_data)
    feedback_df['timestamp'] = pd.to_datetime(feedback_df['timestamp'])

    total_feedback = len(feedback_df)
    helpful_count = (feedback_df['score'] == 1).sum()
    unhelpful_count = (feedback_df['score'] == -1).sum()
    
    helpful_percentage = (helpful_count / total_feedback * 100) if total_feedback > 0 else 0

    fb_cols = st.columns(3)
    fb_cols[0].metric("Total Feedback Received", total_feedback)
    fb_cols[1].metric("Helpful Responses", f"{helpful_count} ({helpful_percentage:.1f}%)")
    fb_cols[2].metric("Unhelpful Responses", unhelpful_count)

    if helpful_count > 0:
        st.markdown("##### Recent Helpful Responses")
        st.dataframe(
            feedback_df[feedback_df['score'] == 1][['query', 'answer']].tail(5),
            use_container_width=True
        )

    if unhelpful_count > 0:
        st.markdown("##### Recent Unhelpful Responses")
        st.dataframe(
            feedback_df[feedback_df['score'] == -1][['query', 'answer']].tail(5),
            use_container_width=True
        )