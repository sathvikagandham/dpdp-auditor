import json
import re
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from dpdp_auditor.ingestion.chunker import extract_chunks

chunks=extract_chunks('data/raw/dpdp_act.pdf')
#chunks=re.split(r'(?=SEC\. \d+\])',full_text)
print(len(chunks))

with open("data/processed/chunks.json","r",encoding="utf-8") as f:
    loaded_data=json.load(f)
    
print(f"Loaded {len(loaded_data)} items.")
for i in range(3):
    print(f"\n--- Chunk {i} ---")
    print(chunks[i][:200])
