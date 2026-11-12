import sys
import os

# Add 'src' to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from dpdp_auditor.agent.llm import get_llm_client

# 1. Get the client
client = get_llm_client()

# 2. The text we want to decompose
policy_text = "We collect your email address and share it with third-party advertisers. We retain your data indefinitely."

# 3. Build a proper prompt
prompt = f"""
You are a legal expert. Break the following text into a list of distinct compliance claims.
Return ONLY a valid JSON list of strings. Do not include markdown formatting like ```json.

Text:
{policy_text}
"""

# 4. Make the API call
print("Calling DeepSeek...")
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": prompt}]
)

# 5. Print the result
print(response.choices[0].message.content)