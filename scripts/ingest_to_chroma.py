import json
import chromadb
from sentence_transformers import SentenceTransformer,util
with open("data/processed/chunks.json","r",encoding="utf-8") as f:
    loading_data=json.load(f)
model=SentenceTransformer("all-MiniLM-L6-v2")
v1=model.encode(loading_data)

client=chromadb.PersistentClient(path="data/processed/chroma_db")
collection=client.get_or_create_collection(name="dpdp_sections",
                                           metadata={"hnsw:space":"cosine"},
                                           )
collection.add(
    ids=[f"chunk_{i}" for i in range(len(loading_data))],
    documents=loading_data,
    embeddings=v1.tolist()
)
print(f"Successfully ingested {len(loading_data)} chunks into ChromaDB.")