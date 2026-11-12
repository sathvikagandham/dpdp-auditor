import sys
import os

# Add the 'src' directory to the path so uvicorn can find dpdp_auditor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import FastAPI
from pydantic import BaseModel

from dpdp_auditor.models.schemas import AuditFinding
from dpdp_auditor.agent.graph import graph


app=FastAPI(title="DPDP Compliance Auditor")

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static",StaticFiles(directory="static"),name="static")

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

class PolicyRequest(BaseModel):
    text:str

@app.post("/audit")
async def run_audit(request: PolicyRequest):
    print(f"Received request: {request.text}")

    initial_state={
        "claim":request.text,
        "law_chunk":"",
        "finding":None,
        "retries":0
    }
    final_state=graph.invoke(initial_state)

    if final_state["finding"]:
        return {"status":"success","finding":final_state["finding"]}
    else:
        return {"status":"failed","message":"No valid finding generated after retries."}
