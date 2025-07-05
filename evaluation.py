# evaluation.py

import os
import json
import requests
import pandas as pd
from typing import List, Dict, Any

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:5000"
QA_DATASET_PATH = os.path.join("app", "data", "evaluation", "qa_dataset.json")
USER_PROFILES_PATH = os.path.join("app", "data", "evaluation", "evaluation_user_profiles.json")
# Path to the file the backend server uses
BACKEND_USER_PROFILES_PATH = os.path.join("app", "data", "evaluation", "user_profiles.json")

def check_server_status():
    """Checks if the backend server is running before starting the evaluation."""
    try:
        # A simple GET request will fail (405 Method Not Allowed), but it proves the server is listening.
        requests.get(BASE_URL + "/api/query", timeout=5)
        print("✅ Backend server is running.")
        return True
    except requests.exceptions.RequestException:
        print("\n❌ CRITICAL: Backend server is not running!")
        print("Please run `python app/main.py` in a separate terminal before starting the evaluation.")
        return False

def evaluate_rag_system(dataset: List[Dict[str, Any]]) -> pd.DataFrame:
    """Evaluates the RAG system's question-answering capabilities."""
    results = []
    print("\n--- Starting RAG System Evaluation ---")

    for i, item in enumerate(dataset):
        question = item['question']
        ideal_keywords = set(item['ideal_answer_keywords'])
        expected_sources = set(item['expected_sources'])
        
        print(f"  Testing Q{i+1}/{len(dataset)}: \"{question[:50]}...\"")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/query",
                json={"query": question, "user_id": "evaluation_service", "chat_history": []},
                timeout=20
            )
            response.raise_for_status()
            data = response.json()
            
            generated_answer = data.get("answer", "").lower()
            retrieved_sources = set(data.get("sources", []))

            matched_keywords = {kw for kw in ideal_keywords if kw in generated_answer}
            answer_score = len(matched_keywords) / len(ideal_keywords) if ideal_keywords else 0

            retrieval_score = len(retrieved_sources.intersection(expected_sources)) / len(expected_sources) if expected_sources else 0
            
        except requests.exceptions.RequestException as e:
            print(f"    ERROR calling API for question: {e}")
            generated_answer, retrieved_sources = "[API Error]", set()
            answer_score, retrieval_score = 0, 0

        results.append({
            "Question": question, "Answer Score": answer_score, "Retrieval Score": retrieval_score
        })
    
    print("--- RAG System Evaluation Complete ---")
    return pd.DataFrame(results)

def evaluate_recommendation_system(user_profiles: List[Dict], qa_dataset: List[Dict]) -> Dict[str, Any]:
    """Evaluates the recommendation system using hold-one-out cross-validation."""
    print("\n--- Starting Recommendation System Evaluation ---")
    
    query_to_topic_map = {item['question']: item['expected_sources'][0] for item in qa_dataset if item['expected_sources']}
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

            try:
                # Prime the system with the current query to update the user's profile
                requests.post(
                    f"{BASE_URL}/api/query",
                    json={"query": current_query, "user_id": user_id, "chat_history": []},
                    timeout=20
                )
                
                # Get recommendations based on the updated profile
                rec_response = requests.post(
                    f"{BASE_URL}/api/recommendations",
                    json={"user_id": user_id},
                    timeout=10
                )
                rec_response.raise_for_status()
                recommendations = rec_response.json().get("recommendations", [])
                recommended_topics = {rec['title'] for rec in recommendations}

                if ground_truth_topic in recommended_topics:
                    successful_hits += 1
                total_prediction_steps += 1

            except requests.exceptions.RequestException as e:
                print(f"    ERROR during recommendation step for user {user_id}: {e}")

    hit_rate = (successful_hits / total_prediction_steps) if total_prediction_steps > 0 else 0
    print("--- Recommendation System Evaluation Complete ---")
    return {"hit_rate": hit_rate, "users_tested": len(user_profiles), "prediction_steps": total_prediction_steps}


if __name__ == "__main__":
    if not check_server_status():
        exit(1)

    # FIX: Ensure a clean state for the evaluation run by deleting the profile
    # file that the backend uses. This makes the recommendation test valid.
    if os.path.exists(BACKEND_USER_PROFILES_PATH):
        print(f"Clearing backend user profiles at '{BACKEND_USER_PROFILES_PATH}' for a clean evaluation.")
        os.remove(BACKEND_USER_PROFILES_PATH)
        
    # --- Load Datasets ---
    try:
        with open(QA_DATASET_PATH, 'r') as f: qa_dataset = json.load(f)
        with open(USER_PROFILES_PATH, 'r') as f: user_profiles_data = json.load(f)
    except FileNotFoundError as e:
        print(f"\n❌ CRITICAL: Could not find a required data file: {e.filename}")
        exit(1)

    # --- Run Evaluations ---
    rag_results_df = evaluate_rag_system(qa_dataset)
    rec_results = evaluate_recommendation_system(user_profiles_data, qa_dataset)

    # --- Print Final Report ---
    print("\n\n" + "="*38)
    print("=== AI SYSTEM EVALUATION REPORT ===")
    print("="*38)

    avg_answer_score = rag_results_df['Answer Score'].mean()
    avg_retrieval_score = rag_results_df['Retrieval Score'].mean()
    print("\n--- RAG System Performance ---")
    print(f"Total Questions Tested: {len(rag_results_df)}")
    print(f"Average Answer Score (Keyword Match): {avg_answer_score:.1%}")
    print(f"Average Retrieval Score (Source Accuracy): {avg_retrieval_score:.1%}")

    print("\n--- Recommendation System Performance ---")
    print(f"User Profiles Tested: {rec_results['users_tested']}")
    print(f"Total Prediction Steps: {rec_results['prediction_steps']}")
    print(f"Recommendation Hit Rate: {rec_results['hit_rate']:.1%}")
    
    print("\n--- Detailed RAG Results ---")
    pd.set_option('display.max_colwidth', 60)
    pd.set_option('display.width', 100)
    print(rag_results_df.to_string(index=False, float_format="%.2f"))

    print("\n" + "="*38 + "\n         END OF REPORT\n" + "="*38)