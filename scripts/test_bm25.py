import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from dpdp_auditor.retrieval.bm25_search import BM25Search

# 1. Load data
with open("data/processed/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# 2. Initialize BM25
bm25 = BM25Search(chunks)

# 3. Search
query = "What is the requirement for giving notice to the Data Principal?"
results = bm25.search(query, top_n=2)

# 4. Print
for i, (score, chunk) in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(f"Score: {score}")
    print(f"Document: {chunk[:300]}...")