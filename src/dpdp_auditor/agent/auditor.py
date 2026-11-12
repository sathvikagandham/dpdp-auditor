import json
from pydantic import ValidationError
from dpdp_auditor.models.schemas import AuditFinding

def audit_claim(claim: str, law_chunk: str, client) -> AuditFinding | None:
    # 1. Build the prompt (use an f-string!)
    prompt = f"""
    You are a DPDP Act compliance auditor. 
    Given the claim and the law, determine if the claim violates the law. 
    Return ONLY a valid JSON object with these exact keys: 
    claim, violated_section, evidence, confidence_score.
    Do not include markdown formatting like ```json.
    
    Claim: {claim}
    Law: {law_chunk}
    """
    
    # 2. Call the LLM
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 3. Get the raw text and clean it
    raw_text = response.choices[0].message.content
    
    # Strip markdown just in case the LLM misbehaves
    clean_text = raw_text.replace("```json", "").replace("```", "").strip()
    
    # 4. Parse and Validate
    try:
        parsed_dict = json.loads(clean_text)
        finding = AuditFinding(**parsed_dict)
        return finding
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"❌ Error parsing LLM output: {e}")
        return None