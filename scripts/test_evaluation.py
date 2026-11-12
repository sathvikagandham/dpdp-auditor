import json
import sys
import os
import chromadb
from sentence_transformers import SentenceTransformer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from dpdp_auditor.retrieval.hybrid_search import HybridSearch
from dpdp_auditor.retrieval.bm25_search import BM25Search

with open("data/processed/test_set.json", "r", encoding="utf-8") as f:
    test_set = json.load(f)
with open("data/processed/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")
bm25 = BM25Search(chunks)

client = chromadb.PersistentClient(path="data/processed/chroma_db")
collection = client.get_or_create_collection(name="dpdp_sections")
hybrid = HybridSearch(bm25_search=bm25, chroma_collection=collection, model=model)

top_k = 3
total_questions = len(test_set)
correct_count = 0

for item in test_set:
    claim = item["claim"]
    expected_section = item["expected_section"] # <--- FIXED: lowercase 's'
    
    hybrid_results = hybrid.search(claim, top_n=top_k)

    # <--- FIXED: Use hybrid_results instead of results
    retrieved_chunks = [chunk_text for chunk_text, score in hybrid_results]

    found = False
    for chunk in retrieved_chunks:
        if chunk.startswith(expected_section):
            found = True
            break
            
    if found:
        correct_count += 1
        print(f"✅ Correct for: {claim}")
    else:
        print(f"❌ Missed for: {claim} (Expected Section {expected_section})")

score = (correct_count / total_questions) * 100
print(f"\nRetrieval Recall@{top_k}: {score:.2f}%")