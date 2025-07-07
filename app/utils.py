# app/utils.py

import json
import threading
import os # <-- ADD THIS IMPORT
from datetime import datetime
from langchain_core.callbacks.base import BaseCallbackHandler
from . import config

# Thread-safe lock for file operations
file_lock = threading.Lock()

# --- Token Usage Callback Handler ---
class TokenUsageCallback(BaseCallbackHandler):
    """Callback to store token usage from LLM calls."""
    def __init__(self):
        super().__init__()
        self._prompt_tokens = []
        self._completion_tokens = []

    def on_llm_end(self, response, **kwargs):
        if response.llm_output and 'token_usage' in response.llm_output:
            usage = response.llm_output['token_usage']
            # Handles different key names for completion tokens in Gemini response
            completion = usage.get('completion_tokens', 0) or usage.get('candidates_token_count', 0)
            self._prompt_tokens.append(usage.get('prompt_token_count', 0))
            self._completion_tokens.append(completion)

    def get_total_prompt_tokens(self):
        return sum(self._prompt_tokens)

    def get_total_completion_tokens(self):
        return sum(self._completion_tokens)

    def get_total_tokens(self):
        return self.get_total_prompt_tokens() + self.get_total_completion_tokens()

    def reset(self):
        self._prompt_tokens = []
        self._completion_tokens = []

# --- User Profile Management ---
def load_user_profiles():
    """Loads user profiles from the JSON file."""
    with file_lock:
        if not os.path.exists(config.USER_PROFILES_PATH):
            return {}
        try:
            # Ensure the directory exists before trying to open the file
            os.makedirs(os.path.dirname(config.USER_PROFILES_PATH), exist_ok=True)
            with open(config.USER_PROFILES_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

def save_user_profiles(profiles):
    """Saves user profiles to the JSON file."""
    with file_lock:
        os.makedirs(os.path.dirname(config.USER_PROFILES_PATH), exist_ok=True)
        with open(config.USER_PROFILES_PATH, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=4)

# --- Logging Functions ---
def log_query(log_entry):
    """Logs a query and its details to a JSONL file."""
    with file_lock:
        with open(config.QUERY_LOGS_PATH, "a", encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")

def log_feedback(log_entry):
    """Logs user feedback to a JSONL file."""
    with file_lock:
        with open(config.FEEDBACK_LOGS_PATH, "a", encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")