import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from dpdp_auditor.models.schemas import AuditFinding
from dpdp_auditor.agent.verifier import verify_finding



# Let's grab a real chunk from your JSON file to use as the law_chunk
with open("data/processed/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)



# Find the chunk that starts with Section 8
law_chunk = next(chunk for chunk in chunks if chunk.startswith("8. "))

valid_finding=AuditFinding(
    claim="We share data with marketing partners.",
    violated_section="8",
    evidence="A Data Fiduciary shall, irrespective of any agreement to the contrary",
    confidence_score=0.9,
    explanation="Section 8 requires data fiduciaries to be responsible."
)

print(f"Result: {verify_finding(valid_finding,law_chunk)}")

print("\n Test2:Hallucinated Finding---")
hallucinated_finding=AuditFinding(
    claim="We share data with marketing partners.",
    violated_section="8",
    evidence="The Data Fiduciary must pay a fine of one million dollars.",
    confidence_score=0.9,
    explanation="Section 8 requires fines."
)

print(f"Result: {verify_finding(hallucinated_finding,law_chunk)}")
