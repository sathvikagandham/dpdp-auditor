import json
import sys
import os
import chromadb
from sentence_transformers import SentenceTransformer,CrossEncoder

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','src')))

from dpdp_auditor.retrieval.hybrid_search import HybridSearch
from dpdp_auditor.retrieval.bm25_search import BM25Search

with open("data/processed/chunks.json","r",encoding="utf-8") as f:
    chunks=json.load(f)

query_text="notice given by the Data Fiduciary before requesting consent"

model=SentenceTransformer("all-MiniLM-L6-v2")
bm25=BM25Search(chunks)


client=chromadb.PersistentClient(path="data/processed/chroma_db")
collection=client.get_or_create_collection(name="dpdp_sections")
hybrid=HybridSearch(bm25_search=bm25,chroma_collection=collection, model= model)

hybrid_results = hybrid.search(query_text,top_n=5)


model_encoder=CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

pairs=[(query_text,chunk) for chunk,rrf_scores in hybrid_results]

rerank_scores=model_encoder.predict(pairs)

final_results=list(zip(rerank_scores,[chunk for chunk,score in hybrid_results]))
final_results.sort(key=lambda x:x[0],reverse=True)

print("\n--Rereanked Results")
for i,(score,chunk) in enumerate(final_results[:2]):
    print(f"\n--Results {i+1}")
    print(f"Rerank score: {score:.4f}")
    print(f"Document: {chunk[:100]}")

