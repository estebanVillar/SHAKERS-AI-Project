# app/metrics_page.py
import streamlit as st
import pandas as pd
import json
import os
import sys
import subprocess
# --- FIX: Use an absolute import from the 'app' package ---
from app import config 

EVALUATION_RESULTS_PATH = "evaluation_results.json"

def run_evaluation():
    """Triggers the evaluation.py script as a subprocess."""
    st.session_state.evaluation_running = True
    st.session_state.evaluation_output = None
    st.session_state.evaluation_results = None
    
    try:
        # Use sys.executable to ensure we use the python from the current venv
        command = [sys.executable, "evaluation.py"]
        with st.spinner("Running full system evaluation... This may take a few minutes."):
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True, # This will raise an error if the script fails
                encoding='utf-8'
            )
            st.session_state.evaluation_output = process.stdout
            # Load the results JSON file created by the script
            if os.path.exists(EVALUATION_RESULTS_PATH):
                with open(EVALUATION_RESULTS_PATH, 'r') as f:
                    st.session_state.evaluation_results = json.load(f)
            st.success("✅ Evaluation complete!")
            
    except subprocess.CalledProcessError as e:
        st.error(f"Evaluation script failed with exit code {e.returncode}.")
        st.session_state.evaluation_output = e.stdout + "\n" + e.stderr
    except FileNotFoundError:
        st.error("Could not find the `evaluation.py` script. Make sure it is in the project root directory.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    
    st.session_state.evaluation_running = False

def reset_metrics():
    """Deletes the log files to reset all metrics."""
    query_log = config.QUERY_LOGS_PATH
    feedback_log = config.FEEDBACK_LOGS_PATH
    
    files_deleted = []
    try:
        if os.path.exists(query_log):
            os.remove(query_log)
            files_deleted.append(os.path.basename(query_log))
        if os.path.exists(feedback_log):
            os.remove(feedback_log)
            files_deleted.append(os.path.basename(feedback_log))
        
        if files_deleted:
            st.success(f"Successfully deleted: {', '.join(files_deleted)}. Metrics have been reset.")
        else:
            st.info("No log files found to delete.")
            
    except Exception as e:
        st.error(f"Could not delete log files: {e}")
    
    # Clear any cached evaluation results as well
    st.session_state.evaluation_results = None
    st.rerun()


def display_metrics():
    """Renders the content of the metrics dashboard."""
    st.header("📊 Metrics Dashboard")
    st.markdown("This dashboard provides real-time insights into the AI's performance, cost, and user satisfaction.")

    # --- NEW: Evaluation Section ---
    st.markdown("---")
    st.subheader("System Quality Evaluation")
    st.markdown("Run a full, objective evaluation of the RAG and Recommendation systems against a ground-truth dataset.")

    if st.button("🚀 Run Full System Evaluation"):
        run_evaluation()
    
    if 'evaluation_results' in st.session_state and st.session_state.evaluation_results:
        results = st.session_state.evaluation_results
        rag_summary = results['rag_summary']
        rec_summary = results['rec_summary']
        
        st.markdown("#### Evaluation Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("RAG Answer Score", f"{rag_summary['avg_answer_score']:.1%}", help="Keyword match accuracy")
        col2.metric("RAG Retrieval Score", f"{rag_summary['avg_retrieval_score']:.1%}", help="Source retrieval accuracy (recall)")
        col3.metric("Rec. Hit Rate", f"{rec_summary['hit_rate']:.1%}", help="Correctly predicted next topic")

        with st.expander("Show Detailed RAG Results"):
            st.dataframe(pd.DataFrame(results['rag_details']), use_container_width=True)

    if 'evaluation_output' in st.session_state and st.session_state.evaluation_output:
        with st.expander("Show Full Evaluation Log"):
            st.code(st.session_state.evaluation_output, language='bash')
            
    # --- QUERY LOGS ---
    st.markdown("---")
    st.subheader("Core Performance & Cost Metrics")
    
    if st.button("🧹 Reset All Metrics & Logs", help="Deletes query_logs.jsonl and feedback_logs.jsonl"):
        reset_metrics()

    log_file_path = config.QUERY_LOGS_PATH
    log_data = []
    try:
        with open(log_file_path, 'r') as f:
            log_data = [json.loads(line) for line in f if line.strip()] 
    except FileNotFoundError:
        st.warning("Query log file not found. Interact with the chat to generate data.")
        display_feedback_metrics()
        return

    if not log_data:
        st.info("No queries have been logged yet.")
    else:
        df = pd.DataFrame(log_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        for col in ['input_tokens', 'output_tokens', 'total_tokens', 'latency_ms', 'cost']:
            if col not in df.columns: df[col] = 0
        for col in ['input_tokens', 'output_tokens', 'total_tokens', 'latency_ms', 'cost']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df[['input_tokens', 'output_tokens', 'total_tokens']] = df[['input_tokens', 'output_tokens', 'total_tokens']].astype(int)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Queries", len(df))
        col2.metric("Avg. Latency (ms)", f"{df['latency_ms'].mean():.0f}")
        total_cost = df['cost'].sum()
        col3.metric("Total Tokens", f"{df['total_tokens'].sum():,}")
        col4.metric(
            "Estimated Cost (USD)", f"${total_cost:.4f}", 
            help=f"Cost is calculated on the backend for the `{config.LLM_MODEL}` model."
        )
        st.subheader("Performance & Usage Over Time")
        chart_data = df.set_index('timestamp')[['latency_ms', 'total_tokens', 'cost']]
        st.line_chart(chart_data)
        st.subheader("Recent Queries Log")
        display_cols = ['timestamp', 'query', 'latency_ms', 'total_tokens', 'cost', 'sources']
        st.dataframe(df[display_cols].tail(10), use_container_width=True)

    display_feedback_metrics()


def display_feedback_metrics():
    """Helper function to display feedback metrics."""
    st.markdown("---")
    st.subheader("User Feedback Metrics")
    feedback_file_path = config.FEEDBACK_LOGS_PATH
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
    fb_cols[2].metric("Satisfaction Score", f"{satisfaction_score:.1f}%", help="((Helpful - Unhelpful) / Total) * 100")

    if unhelpful_count > 0:
        st.markdown("##### Recent Unhelpful Responses")
        st.dataframe(feedback_df[feedback_df['score'] == -1][['query', 'answer']].tail(5), use_container_width=True, hide_index=True)