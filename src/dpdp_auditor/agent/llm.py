from openai import OpenAI
import sys
import os

# Import your config function
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from dpdp_auditor.config import get_api_key

def get_llm_client():
    # 1. Fetch the key safely
    api_key = get_api_key()
    
    # 2. Return the client (Clean, no proxy)
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )