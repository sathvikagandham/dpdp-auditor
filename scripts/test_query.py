import chromadb
from sentence_transformers import SentenceTransformer

model=SentenceTransformer("all-MiniLM-L6-v2")
query_text = "What is the requirement for giving notice to the Data Principal?"
query_vector=model.encode(query_text).tolist()

client = chromadb.PersistentClient(path="data/processed/chroma_db")
collection = client.get_or_create_collection(name="dpdp_sections")

results = collection.query(
    query_embeddings=[query_vector],
    n_results=2
)
# Loop through the 2 results
for i in range(2):
    print(f"\n--- Result {i+1} ---")
    print(f"Distance: {results['distances'][0][i]}")
    print(f"Document: {results['documents'][0][i][:300]}...")