import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from dpdp_auditor.agent.llm import get_llm_client
from dpdp_auditor.agent.auditor import audit_claim

# 1. Setup Client
client = get_llm_client()

# 2. Setup Data
claim = "We share user data with marketing partners."

# Let's grab a real chunk from your JSON file to use as the law_chunk
with open("data/processed/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)



# Find the chunk that starts with Section 8
law_chunk = next(chunk for chunk in chunks if chunk.startswith("8. "))

# 3. Run the Auditor
print("Auditing claim...")
result = audit_claim(claim, law_chunk, client)

# 4. Print Result
if result:
    print("\n✅ Valid AuditFinding Generated!")
    print(f"Claim: {result.claim}")
    print(f"Violated Section: {result.violated_section}")
    print(f"Confidence: {result.confidence_score}")
    print(f"Explanation: {result.explanation}")
else:
    print("\n❌ Audit failed. Check the error above.")
    