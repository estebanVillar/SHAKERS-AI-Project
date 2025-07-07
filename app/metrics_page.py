# app/metrics_page.py
import streamlit as st
import pandas as pd
import json
import os

def display_metrics():
    """Renders the content of the metrics dashboard."""
    st.header("📊 Metrics Dashboard")
    st.markdown("This dashboard provides real-time insights into the AI's performance, cost, and user satisfaction.")

    # --- QUERY LOGS ---
    st.subheader("Core Performance & Cost Metrics")
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "query_logs.jsonl")
    log_data = []
    try:
        with open(log_file_path, 'r') as f:
            # Added check for empty lines to prevent JSON errors
            log_data = [json.loads(line) for line in f if line.strip()] 
    except FileNotFoundError:
        st.warning("Query log file not found. Interact with the chat to generate data.")
        st.markdown("---") 
        st.subheader("User Feedback Metrics")
        display_feedback_metrics() # Still show feedback section
        return

    if not log_data:
        st.info("No queries have been logged yet.")
    else:
        df = pd.DataFrame(log_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Ensure token columns exist, filling with 0 for backward compatibility
        for col in ['input_tokens', 'output_tokens', 'total_tokens', 'latency_ms']:
            if col not in df.columns:
                df[col] = 0
        
        # Convert to numeric, handling potential errors
        for col in ['input_tokens', 'output_tokens', 'total_tokens', 'latency_ms']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df[['input_tokens', 'output_tokens', 'total_tokens']] = df[['input_tokens', 'output_tokens', 'total_tokens']].astype(int)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Queries", len(df))
        col2.metric("Avg. Latency (ms)", f"{df['latency_ms'].mean():.0f}")
        
        # Cost calc for gemini-1.5-flash: $0.125/M input, $0.375/M output tokens
        input_cost = (df['input_tokens'].sum() / 1_000_000) * 0.125
        output_cost = (df['output_tokens'].sum() / 1_000_000) * 0.375
        total_cost = input_cost + output_cost
        col3.metric("Total Tokens", f"{df['total_tokens'].sum():,}")
        col4.metric("Estimated Cost", f"${total_cost:.4f}", help="Based on gemini-1.5-flash pricing as of late 2024.")

        st.subheader("Performance & Usage Over Time")
        chart_data = df.set_index('timestamp')[['latency_ms', 'total_tokens']]
        st.line_chart(chart_data)

        st.subheader("Recent Queries Log")
        display_cols = ['timestamp', 'query', 'latency_ms', 'total_tokens', 'input_tokens', 'output_tokens', 'sources']
        st.dataframe(df[display_cols].tail(10), use_container_width=True)

    # --- FEEDBACK METRICS ---
    st.markdown("---")
    st.subheader("User Feedback Metrics")
    display_feedback_metrics()


def display_feedback_metrics():
    """Helper function to display feedback metrics."""
    feedback_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "feedback_logs.jsonl")
    feedback_data = []
    try:
        with open(feedback_file_path, 'r') as f:
            feedback_data = [json.loads(line) for line in f if line.strip()]
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
    
    satisfaction_score = ((helpful_count - unhelpful_count) / total_feedback * 100) if total_feedback > 0 else 0

    fb_cols = st.columns(3)
    fb_cols[0].metric("Total Feedback", total_feedback)
    fb_cols[1].metric("Helpful", f"{helpful_count}")
    fb_cols[2].metric("Satisfaction Score", f"{satisfaction_score:.1f}%", 
                     help="((Helpful - Unhelpful) / Total) * 100")

    if unhelpful_count > 0:
        st.markdown("##### Recent Unhelpful Responses")
        st.dataframe(
            feedback_df[feedback_df['score'] == -1][['query', 'answer']].tail(5),
            use_container_width=True, hide_index=True
        )