from dpdp_auditor.models.schemas import AuditFinding
import re

def verify_finding(finding: AuditFinding, user_policy: str, law_chunk: str) -> bool:
    # 1. Check for missing defaults
    if not finding.violated_section or not finding.policy_evidence or not finding.legal_evidence:
        return False
        
    # 2. Verify Section Number exists (e.g., extract '8' from 'Section 8')
    section_num = re.search(r'\d+', finding.violated_section)
    if not section_num or section_num.group() not in law_chunk:
        return False
        
    # 3. Verify Policy Evidence exists in user's submitted text
    if finding.policy_evidence.lower().strip() not in user_policy.lower():
        print("❌ Policy evidence hallucinated or not exact.")
        return False
        
    # 4. Verify Legal Evidence exists in retrieved law chunk
    if finding.legal_evidence.lower().strip() not in law_chunk.lower():
        print("❌ Legal evidence hallucinated or not exact.")
        return False
        
    return True


 

