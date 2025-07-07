# app/config.py

import os

# --- Base Directories ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
CACHE_DIR = os.path.join(BASE_DIR, 'cache')

# --- File Paths ---
VECTORSTORE_PATH = os.path.join(CACHE_DIR, 'faiss_pdr_index')
DOCSTORE_PATH = os.path.join(CACHE_DIR, 'pdr_docstore.pkl')
KNOWLEDGE_BASE_PATH = os.path.join(PROJECT_ROOT, 'data/knowledge_base')
USER_PROFILES_PATH = os.path.join(BASE_DIR, 'data', 'evaluation', 'user_profiles.json')
QUERY_LOGS_PATH = os.path.join(PROJECT_ROOT, 'query_logs.jsonl')
FEEDBACK_LOGS_PATH = os.path.join(PROJECT_ROOT, 'feedback_logs.jsonl')
# NEW: Path to the few-shot examples
FEW_SHOT_EXAMPLES_PATH = os.path.join(BASE_DIR, 'data', 'evaluation', 'few_shot_examples.json')
# NEW: Path to the main system prompt template
KNOWLEDGE_BASE_INSTRUCTIONS_PATH = os.path.join(BASE_DIR, 'prompt')


# --- Model & Embedding Configuration ---
EMBEDDING_MODEL = "models/embedding-001"
LLM_MODEL = "gemini-2.0-flash"
LLM_TEMPERATURE = 0.2

# --- RAG Configuration ---
PARENT_CHUNK_SIZE = 2000
PARENT_CHUNK_OVERLAP = 200
CHILD_CHUNK_SIZE = 400
CHILD_CHUNK_OVERLAP = 50

# --- Recommendation Configuration ---
RECOMMENDATION_THRESHOLD_HIGH = 0.45
RECOMMENDATION_THRESHOLD_LOW = 0.35
MAX_RECOMMENDATIONS = 3