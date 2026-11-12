import sys
import os
import pydantic_core

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','src')))

from dpdp_auditor.models.schemas import AuditFinding
valid_finding=AuditFinding(
    claim="We collect email addresses for account creation.",
    violated_section="Section 5(1)",
    evidence="Every request made to a Data Principal...",
    confidence_score=0.95,
    explanation="Notice is required for data collection."
)
print(valid_finding)

print("\n--- Testing invalid (confidence > 1.0) ---")
invalid_finding=AuditFinding(
    claim="We collect email addresses for account creation.",
    violated_section="Section 5(1)",
    evidence="Every request made to a Data Principal...",
    confidence_score=1.5,
    explanation="Notice is required for data collection."
)