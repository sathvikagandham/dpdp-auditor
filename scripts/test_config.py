import sys
import os

# Add the 'src' directory to the path so we can import our package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from dpdp_auditor.config import get_api_key

if __name__ == "__main__":
    try:
        key = get_api_key()
        # We only print the first 5 characters so we don't leak the whole key in the logs
        print(f"✅ API Key loaded successfully: {key[:5]}...")
    except Exception as e:
        print(f"❌ Error: {e}")