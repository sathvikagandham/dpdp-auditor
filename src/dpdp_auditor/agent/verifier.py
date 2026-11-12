import json
from pydantic import ValidationError
from dpdp_auditor.models.schemas import AuditFinding
from dpdp_auditor.agent.auditor import audit_claim



def verify_finding(finding:AuditFinding,law_chunk:str) ->bool:
    if finding.violated_section=="Unknown Section" or finding.evidence=="No evidence provided":
        return False
    if finding.violated_section.lower() not in law_chunk.lower():
        return False
    if finding.evidence.lower().strip() not in law_chunk.lower():
        return False
    return True



 

