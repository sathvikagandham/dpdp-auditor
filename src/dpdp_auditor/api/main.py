import sys
import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add the 'src' directory to the path so uvicorn can find dpdp_auditor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dpdp_auditor.agent.graph import graph
from dpdp_auditor.agent.llm import get_llm_client

app = FastAPI(title="DPDP Compliance Auditor")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

class PolicyRequest(BaseModel):
    text: str

def decompose_policy(policy_text: str) -> list[str]:
    """Uses the LLM to break a privacy policy into individual claims."""
    client = get_llm_client()
    
    prompt = f"""
    You are a legal expert. Break the following text into a list of distinct compliance claims.
    Return ONLY a valid JSON list of strings. Do not include markdown formatting like ```json.
    
    Text:
    {policy_text}
    """
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b", # or your Groq model name
            messages=[{"role": "user", "content": prompt}]
        )
        raw_text = response.choices[0].message.content
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        claims = json.loads(clean_text)
        
        # Ensure it's a list of strings
        if isinstance(claims, list):
            return claims
        return [policy_text] # Fallback if LLM fails to return a list
        
    except Exception as e:
        print(f"❌ Decomposition failed: {e}. Falling back to single claim.")
        return [policy_text]

@app.post("/audit")
async def run_audit(request: PolicyRequest):
    print(f"\nReceived request: {request.text}")
    
    # 1. Break the policy into individual claims
    print("Decomposing policy into claims...")
    claims = decompose_policy(request.text)
    print(f"Claims found: {claims}")
    
    all_findings = []
    
    # 2. Loop through each claim and run the LangGraph agent
    for claim in claims:
        print(f"\nAuditing claim: {claim}")
        
        initial_state = {
            "claim": claim,
            "law_chunk": "",
            "finding": None,
            "retries": 0
        }
        
        # Run the graph for this specific claim
        final_state = graph.invoke(initial_state)
        
        # If a valid, verified finding was generated, add it to our list
        if final_state["finding"]:
            all_findings.append(final_state["finding"])
    
    # 3. Return the results
    if all_findings:
        return {
            "status": "success", 
            "total_claims": len(claims),
            "violations_found": len(all_findings),
            "findings": all_findings
        }
    else:
        return {
            "status": "failed", 
            "message": "No valid findings generated after retries.",
            "total_claims": len(claims)
        }