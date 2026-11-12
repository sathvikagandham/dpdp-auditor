from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import json
import chromadb
from sentence_transformers import SentenceTransformer

# Import your custom modules
from dpdp_auditor.retrieval.hybrid_search import HybridSearch
from dpdp_auditor.retrieval.bm25_search import BM25Search
from dpdp_auditor.agent.llm import get_llm_client
from dpdp_auditor.agent.auditor import audit_claim
from dpdp_auditor.agent.verifier import verify_finding
from dpdp_auditor.models.schemas import AuditFinding

# 1. Setup LLM (this is lightweight, just an API wrapper, so it can stay here)
llm_client = get_llm_client()

class AgentState(TypedDict):
    claim: str
    law_chunk: str
    finding: dict | None
    retries: int

# --- GLOBAL CACHE FOR HEAVY MODELS ---
# We use these to store the models after they load the first time.
_model = None
_bm25 = None
_collection = None

def get_search_engines():
    """Lazy loads the heavy models only when needed."""
    global _model, _bm25, _collection
    
    # If they are not loaded yet, load them
    if _model is None:
        print("  [System] Lazy loading SentenceTransformer and ChromaDB...")
        with open("data/processed/chunks.json", "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _bm25 = BM25Search(chunks)
        chroma_client = chromadb.PersistentClient(path="data/processed/chroma_db")
        _collection = chroma_client.get_or_create_collection(name="dpdp_sections")
        
    return HybridSearch(bm25_search=_bm25, chroma_collection=_collection, model=_model)

# --- NODES ---

def retrieve_node(state: AgentState):
    print(f"  [Retrieve Node] Searching for: {state['claim']}")
    
    # Load the search engines (this will only take time on the very first request)
    hybrid = get_search_engines()
    
    results = hybrid.search(state["claim"], top_n=1)
    chunk_text = results[0][0]
    return {"law_chunk": chunk_text}

def audit_node(state: AgentState):
    print(f"  [Audit Node] Auditing claim against law...")
    finding_obj = audit_claim(state["claim"], state["law_chunk"], llm_client)
    
    if finding_obj:
        return {"finding": finding_obj.model_dump()}
    else:
        return {"finding": None}

def verify_node(state: AgentState):
    print("  [Verify Node] Verifying evidence against law...")
    if state["finding"] is None:
        return state

    finding_obj = AuditFinding(**state["finding"])
    is_valid = verify_finding(finding_obj, state["law_chunk"])

    if not is_valid:
        print("  [Verify Node] ❌ Verification FAILED. Evidence is hallucinated.")
        return {"finding": None}
    else:
        print("  [Verify Node] ✅ Verification PASSED.")
        return state

def fallback_node(state: AgentState):
    print("  [Fallback Node] Audit failed. Retrying...")
    new_retries = state["retries"] + 1
    return {"retries": new_retries}

def should_retry(state: AgentState):
    if state["finding"] is not None:
        return "end"
    if state["retries"] >= 2:
        return "end"
    return "retry"

# --- BUILD THE GRAPH ---
builder = StateGraph(AgentState)

builder.add_node("retrieve", retrieve_node)
builder.add_node("audit", audit_node)
builder.add_node("verify", verify_node)
builder.add_node("fallback", fallback_node)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "audit")
builder.add_edge("audit", "verify")

builder.add_conditional_edges(
    "verify",
    should_retry,
    {
        "end": END,
        "retry": "fallback"
    }
)

builder.add_edge("fallback", "retrieve")

graph = builder.compile()