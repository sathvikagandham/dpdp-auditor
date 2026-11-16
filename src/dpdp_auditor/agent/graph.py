from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import json
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder

# Import your custom modules
from dpdp_auditor.retrieval.hybrid_search import HybridSearch
from dpdp_auditor.retrieval.bm25_search import BM25Search
from dpdp_auditor.agent.llm import get_llm_client
from dpdp_auditor.agent.auditor import audit_claim
from dpdp_auditor.agent.verifier import verify_finding
from dpdp_auditor.models.schemas import AuditFinding

llm_client = get_llm_client()

class AgentState(TypedDict):
    claim: str
    law_chunk: str
    finding: dict | None
    retries: int

# --- GLOBAL CACHE FOR HEAVY MODELS ---
_model = None
_bm25 = None
_collection = None
_cross_encoder = None

def get_search_engines():
    """Lazy loads the heavy models only when needed."""
    global _model, _bm25, _collection, _cross_encoder
    
    if _model is None:
        print("  [System] Lazy loading SentenceTransformer and ChromaDB...")
        with open("data/processed/chunks.json", "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _bm25 = BM25Search(chunks)
        chroma_client = chromadb.PersistentClient(path="data/processed/chroma_db")
        _collection = chroma_client.get_or_create_collection(name="dpdp_sections")
        
    if _cross_encoder is None:
        print("  [System] Lazy loading CrossEncoder...")
        _cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
    return HybridSearch(bm25_search=_bm25, chroma_collection=_collection, model=_model)

# --- NODES ---

def retrieve_node(state: AgentState):
    print(f"  [Retrieve Node] Searching for: {state['claim']} (Attempt {state['retries'] + 1})")
    
    hybrid = get_search_engines()
    
    # Dynamically expand retrieval on retries
    dynamic_top_n = 5 + (state["retries"] * 5)
    results = hybrid.search(state["claim"], top_n=dynamic_top_n)
    chunk_texts = [chunk for chunk, score in results]

    if not chunk_texts:
        return {"law_chunk": ""}
    
    pairs = [(state["claim"], chunk) for chunk in chunk_texts]
    rerank_scores = _cross_encoder.predict(pairs)

    best_index = rerank_scores.argmax()
    best_chunk = chunk_texts[best_index]

    return {"law_chunk": best_chunk}

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
    
    # Pass both the claim (user policy) and law_chunk to the verifier
    is_valid = verify_finding(finding_obj, state["claim"], state["law_chunk"])

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