# evaluation.py

import os
import json
import requests
import pandas as pd
from typing import List, Dict, Any
from app import utils

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:5000"
QA_DATASET_PATH = os.path.join("app", "data", "evaluation", "qa_dataset.json")
USER_PROFILES_PATH = os.path.join("app", "data", "evaluation", "evaluation_user_profiles.json")
BACKEND_USER_PROFILES_PATH = os.path.join("app", "data", "user_profiles.json")
EVALUATION_RESULTS_PATH = "evaluation_results.json"

def check_server_status():
    """Checks if the backend server is running before starting the evaluation."""
    try:
        response = requests.post(BASE_URL + "/api/query", json={}, timeout=3)
        if response.status_code == 400:
             print("OK: Backend server is running.")
             return True
        return False
    except requests.exceptions.RequestException:
        print("\n CRITICAL: Backend server is not running!")
        print("Please run `python app/main.py` in a separate terminal before starting the evaluation.")
        return False

def evaluate_rag_system(dataset: List[Dict[str, Any]]) -> pd.DataFrame:
    """Evaluates the RAG system's question-answering capabilities."""
    results = []
    print("\n--- Starting RAG System Evaluation ---")

    for i, item in enumerate(dataset):
        question = item['question']
        ideal_keywords = set(kw.lower() for kw in item['ideal_answer_keywords'])
        # +++ THE FIX: Call the function from the utils module +++
        expected_sources = {utils.normalize_topic(s) for s in item['expected_sources']}
        
        print(f"  Testing Q{i+1}/{len(dataset)}: \"{question[:50]}...\"")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/query",
                json={"query": question, "user_id": "evaluation_service", "chat_history": []},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            generated_answer = data.get("answer", "").lower()
            retrieved_sources_raw = data.get("sources", [])
            # +++ THE FIX: Call the function from the utils module +++
            retrieved_sources = {utils.normalize_topic(s) for s in retrieved_sources_raw if s and s != "None"}

            matched_keywords = {kw for kw in ideal_keywords if kw in generated_answer}
            answer_score = len(matched_keywords) / len(ideal_keywords) if ideal_keywords else 0

            retrieval_score = len(retrieved_sources.intersection(expected_sources)) / len(expected_sources) if expected_sources else 0
            
        except requests.exceptions.RequestException as e:
            print(f"    ERROR calling API for question: {e}")
            generated_answer, retrieved_sources = "[API Error]", set()
            answer_score, retrieval_score = 0, 0

        results.append({
            "Question": question, "Answer Score": answer_score, "Retrieval Score": retrieval_score,
            "Retrieved Sources": ", ".join(sorted(list(retrieved_sources))) or "None"
        })
    
    print("--- RAG System Evaluation Complete ---")
    return pd.DataFrame(results)

def evaluate_recommendation_system(user_profiles: List[Dict], qa_dataset: List[Dict]) -> Dict[str, Any]:
    """Evaluates the recommendation system using hold-one-out cross-validation."""
    print("\n--- Starting Recommendation System Evaluation ---")

    query_to_topic_map = {
        item['question']: utils.normalize_topic(item['expected_sources'][0]) 
        for item in qa_dataset if item.get('expected_sources')
    }
    total_prediction_steps, successful_hits = 0, 0

    for user in user_profiles:
        user_id = user['user_id']
        query_history = user['query_history']
        print(f"  Testing User Profile: {user_id} ({len(query_history)} queries)")

        if len(query_history) < 2: continue

        for i in range(len(query_history) - 1):
            current_query = query_history[i]
            next_query = query_history[i+1]
            ground_truth_topic = query_to_topic_map.get(next_query)
            if not ground_truth_topic: continue

            total_prediction_steps += 1
            try:
                requests.post(
                    f"{BASE_URL}/api/query",
                    json={"query": current_query, "user_id": user_id, "chat_history": []},
                    timeout=30
                )
                
                rec_response = requests.post(f"{BASE_URL}/api/recommendations", json={"user_id": user_id}, timeout=10)
                rec_response.raise_for_status()
                recommendations = rec_response.json().get("recommendations", [])
                
              
                recommended_topics = {utils.normalize_topic(rec['topic_id']) for rec in recommendations}

                if ground_truth_topic in recommended_topics:
                    successful_hits += 1

            except requests.exceptions.RequestException as e:
                print(f"    ERROR during recommendation step for user {user_id}: {e}")

    hit_rate = (successful_hits / total_prediction_steps) if total_prediction_steps > 0 else 0
    print("--- Recommendation System Evaluation Complete ---")
    return {"hit_rate": hit_rate, "users_tested": len(user_profiles), "prediction_steps": total_prediction_steps}


if __name__ == "__main__":
    if not check_server_status():
        exit(1)

    if os.path.exists(BACKEND_USER_PROFILES_PATH):
        print(f"Clearing backend user profiles at '{BACKEND_USER_PROFILES_PATH}' for a clean evaluation.")
        os.remove(BACKEND_USER_PROFILES_PATH)
        
    try:
        with open(QA_DATASET_PATH, 'r') as f: qa_dataset = json.load(f)
        with open(USER_PROFILES_PATH, 'r') as f: user_profiles_data = json.load(f)
    except FileNotFoundError as e:
        print(f"\n CRITICAL: Could not find a required data file: {e.filename}")
        exit(1)

    rag_results_df = evaluate_rag_system(qa_dataset)
    rec_results = evaluate_recommendation_system(user_profiles_data, qa_dataset)
    
    avg_answer_score = rag_results_df['Answer Score'].mean()
    avg_retrieval_score = rag_results_df['Retrieval Score'].mean()

    final_report = {
        "rag_summary": {
            "total_questions": len(rag_results_df),
            "avg_answer_score": avg_answer_score,
            "avg_retrieval_score": avg_retrieval_score
        },
        "rec_summary": {
            "users_tested": rec_results['users_tested'],
            "prediction_steps": rec_results['prediction_steps'],
            "hit_rate": rec_results['hit_rate']
        },
        "rag_details": rag_results_df.to_dict(orient='records')
    }
    
    with open(EVALUATION_RESULTS_PATH, 'w') as f:
        json.dump(final_report, f, indent=4)
    print(f"\nOK: Evaluation results saved to '{EVALUATION_RESULTS_PATH}'")

    print("\n\n" + "="*38)
    print("=== AI SYSTEM EVALUATION REPORT ===")
    print("="*38)
    print("\n--- RAG System Performance ---")
    print(f"Total Questions Tested: {final_report['rag_summary']['total_questions']}")
    print(f"Average Answer Score (Keyword Match): {final_report['rag_summary']['avg_answer_score']:.1%}")
    print(f"Average Retrieval Score (Source Accuracy): {final_report['rag_summary']['avg_retrieval_score']:.1%}")
    print("\n--- Recommendation System Performance ---")
    print(f"User Profiles Tested: {final_report['rec_summary']['users_tested']}")
    print(f"Total Prediction Steps: {final_report['rec_summary']['prediction_steps']}")
    print(f"Recommendation Hit Rate: {final_report['rec_summary']['hit_rate']:.1%}")
    print("\n--- Detailed RAG Results ---")
    pd.set_option('display.max_colwidth', 50)
    pd.set_option('display.width', 120)
    print(rag_results_df.to_string(index=False, float_format="%.2f"))
    print("\n" + "="*38 + "\n         END OF REPORT\n" + "="*38)
