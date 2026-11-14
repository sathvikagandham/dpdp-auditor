from pydantic import BaseModel,Field

class AuditFinding(BaseModel):
    claim:str
    policy_evidence:str=Field(description="Exact quote from the user's policy")
    legal_evidence:str=Field(description="Exact quote from the DPDP Act")
    violated_section:str=Field(description="The section number,e.g./ 'SEction 8'")
    confidence_score:float=Field(ge=0.0, le=1.0)
    explanation:str
