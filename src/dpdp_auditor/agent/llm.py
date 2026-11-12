from openai import OpenAI
import httpx # <-- Import thi
import sys
import os

# Import your config function
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from dpdp_auditor.config import get_api_key

def get_llm_client():
    # 1. Fetch the key safely
    api_key = get_api_key()

    proxy_url = "http://B210693:7M3QXK@studentnet.rgukt.ac.in:3128"

    http_client = httpx.Client(
        proxy=proxy_url,    # Explicitly tell httpx to use this proxy
        trust_env=False     # Ignore other proxy environment variables
    )
    
    # 2. Return the client
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        http_client=http_client # <-- Pass it here
    )