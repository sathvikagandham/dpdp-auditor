import json
import sys
import os
import chromadb
from sentence_transformers import SentenceTransformer,CrossEncoder

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','src')))

from dpdp_auditor.agent.llm import get_llm_client

client=get_llm_client()
policy_text="We collect email addresses for account creation. We share user data with our marketing partners. We store data indefinitely."

# 3. Build a proper prompt
prompt = f"""
You are a legal expert. Break the following text into a list of distinct compliance claims.
Return ONLY a valid JSON list of strings. Do not include markdown formatting like ```json.

Text:
{policy_text}
"""
# 4. Make the API call
print("Calling DeepSeek...")
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": prompt}]
)

from dpdp_auditor.retrieval.hybrid_search import HybridSearch
from dpdp_auditor.retrieval.bm25_search import BM25Search

with open("data/processed/chunks.json","r",encoding="utf-8") as f:
    chunks=json.load(f)

model=SentenceTransformer("all-MiniLM-L6-v2")
bm25=BM25Search(chunks)

llm_output = response.choices[0].message.content
claims=json.loads(llm_output)

client=chromadb.PersistentClient(path="data/processed/chroma_db")
collection=client.get_or_create_collection(name="dpdp_sections")
hybrid=HybridSearch(bm25_search=bm25,chroma_collection=collection, model= model)



for claim in claims:
    hybrid_results = hybrid.search(claim,top_n=1)
    best_chunk=hybrid_results[0][0]

    print(f"\n claim: {claim}")
    print(f" Match: {best_chunk[:200]}...")