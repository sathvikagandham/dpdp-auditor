from pydantic import BaseModel,Field

class AuditFinding(BaseModel):
    claim:str
    violated_section:str=Field(default="Unknown Section")
    evidence:str = Field(default="No evidence provided")
    confidence_score:float=Field(default=0.0, ge=0.0, le=1.0)
    explanation:str=Field(default="No explanation provided")
