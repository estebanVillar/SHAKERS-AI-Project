# app/utils.py

import json
import threading
import os
from datetime import datetime
from langchain_core.callbacks.base import BaseCallbackHandler
from . import config

# Thread-safe lock for file operations
file_lock = threading.Lock()

# +++ THE FIX: This function is now in the correct shared utility file +++
def normalize_topic(topic: str) -> str:
    """Cleans a topic name by removing path prefixes and file extensions."""
    if not isinstance(topic, str):
        return ""
    base_name = os.path.basename(topic)
    name_without_ext = os.path.splitext(base_name)[0]
    return name_without_ext.strip()

# --- Token Usage Callback Handler ---
class TokenUsageCallback(BaseCallbackHandler):
    """
    Callback to parse and store token usage from LLM calls,
    specifically designed to be robust for Google Gemini models.
    """
    def __init__(self):
        super().__init__()
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def on_llm_end(self, response, **kwargs):
        """
        Parses the response from the LLM to find token information.
        """
        for generation_chunk in response.generations:
            for generation in generation_chunk:
                if generation.generation_info:
                    usage = generation.generation_info.get('usage_metadata', {})
                    if usage:
                        self.prompt_tokens += usage.get('input_tokens', 0)
                        self.completion_tokens += usage.get('output_tokens', 0)

    def get_total_prompt_tokens(self):
        return self.prompt_tokens

    def get_total_completion_tokens(self):
        return self.completion_tokens

    def get_total_tokens(self):
        return self.get_total_prompt_tokens() + self.get_total_completion_tokens()

    def reset(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0

# --- Cost Calculation Utility ---
def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculates the cost of an LLM call based on token usage and config prices."""
    input_cost = (input_tokens / 1_000_000) * config.INPUT_TOKEN_PRICE_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * config.OUTPUT_TOKEN_PRICE_PER_MILLION
    total_cost = input_cost + output_cost
    return total_cost

# --- User Profile Management ---
def load_user_profiles():
    """Loads user profiles from the JSON file."""
    with file_lock:
        profile_path = os.path.join(config.BASE_DIR, 'data', 'user_profiles.json')
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        if not os.path.exists(profile_path):
            return {}
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

def save_user_profiles(profiles):
    """Saves user profiles to the JSON file."""
    with file_lock:
        profile_path = os.path.join(config.BASE_DIR, 'data', 'user_profiles.json')
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        with open(profile_path, 'w', encoding='utf-8') as f:
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