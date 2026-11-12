import json
import os
import sys
from sentence_transformers import SentenceTransformer
import chromadb

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','src')))
from dpdp_auditor.retrieval.bm25_search import BM25Search
from dpdp_auditor.retrieval.hybrid_search import HybridSearch

query = "notice given by the Data Fiduciary before requesting consent"

rrf_scores={}

with open("data/processed/chunks.json","r",encoding="utf-8") as f:
    chunks=json.load(f)


model=SentenceTransformer("all-MiniLM-L6-v2")
bm25=BM25Search(chunks)
client=chromadb.PersistentClient(path="data/processed/chroma_db")
collection=client.get_or_create_collection(name="dpdp_sections")

hybrid=HybridSearch(bm25_search=bm25,chroma_collection=collection,model=model)
results = hybrid.search(query,top_n=5)

for i,(chunk,rrf_score) in enumerate(results):
    print(f"\n---Result {i+1}")
    print(f"RRF Score : {rrf_score}")
    print(f"Document: {chunk[:300]}...")

