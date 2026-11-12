from langgraph.graph import StateGraph,START,END
from typing import TypedDict

import json
import chromadb
from sentence_transformers import SentenceTransformer,CrossEncoder

from dpdp_auditor.retrieval.hybrid_search import HybridSearch
from dpdp_auditor.retrieval.bm25_search import BM25Search
from dpdp_auditor.agent.llm import get_llm_client
from dpdp_auditor.agent.auditor import audit_claim

from dpdp_auditor.agent.verifier import verify_finding

with open("data/processed/chunks.json","r",encoding="utf-8") as f:
    chunks=json.load(f)

bm25=BM25Search(chunks)
model=SentenceTransformer("all-MiniLM-L6-v2")
chroma_client=chromadb.PersistentClient(path="data/processed/chroma_db")
collection=chroma_client.get_or_create_collection(name="dpdp_sections")
hybrid=HybridSearch(bm25_search=bm25,chroma_collection=collection,model=model)
llm_client=get_llm_client()

class AgentState(TypedDict):
    claim:str
    law_chunk:str
    finding:dict |None
    retries:int

def retrieve_node(state:AgentState):
    results=hybrid.search(state["claim"],top_n=1)

    chunk_text=results[0][0]
    return {"law_chunk":chunk_text}

def audit_node(state: AgentState):

    finding_obj=audit_claim(state["claim"],state["law_chunk"],llm_client)
    if finding_obj:
        return {"finding":finding_obj.model_dump()}
    else:
        return {"finding":None}

def fallback_node(state:AgentState):
    new_retries=state["retries"]+1
    return {"retries":new_retries}

def verify_node(state: AgentState):
    print(" [Verify Node] Verifying evidence against law...")
    if state["finding"] is None:
        return state

    from dpdp_auditor.models.schemas import AuditFinding
    finding_obj= AuditFinding(**state["finding"])

    is_valid=verify_finding(finding_obj,state["law_chunk"])

    if not is_valid:
      print(" [Verify Node] ❌ verification FAI LED. Evidence is hallucinated.")
      return {"finding":None} 
    else:
      print(" [Verify Node] ✅ Verification PASSED.")
      return state
def should_retry(state:AgentState):
    if state["finding"] is not None:
        return "end"
    if state["retries"]>=2:
        return "end"
    return "retry"

builder=StateGraph(AgentState)
builder.add_node("retrieve",retrieve_node)
builder.add_node("audit",audit_node)
builder.add_node("verify",verify_node)
builder.add_node("fallback",fallback_node)

builder.add_edge(START,"retrieve")
builder.add_edge("retrieve","audit")
builder.add_edge("audit","verify")

builder.add_conditional_edges(
    #"audit",
    "verify",
    should_retry,
    {
        "end":END,
        "retry":"fallback"
    }
)

builder.add_edge("fallback","retrieve")

graph=builder.compile()