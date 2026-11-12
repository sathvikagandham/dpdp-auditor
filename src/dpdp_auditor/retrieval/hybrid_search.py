class HybridSearch:
    def __init__(self,bm25_search,chroma_collection,model):
        self.bm25=bm25_search
        self.collection=chroma_collection
        self.model=model
    def search(self,query:str,top_n:int=2):
        #1. get BM25 results top5
        bm25_results=self.bm25.search(query,top_n=5)
        #2. get vector results top5
        query_vector=self.model.encode(query).tolist()

        vector_results=self.collection.query(
            query_embeddings=[query_vector],
            n_results=5
        )

        #3. initialize rrf dictioanry to accumulate scores
        rrf_scores={}

        #4. add BM25_results is a list of tuples:(score,chunk_text)
        for rank,(score,chunk) in enumerate(bm25_results):
            rrf_scores[chunk] = rrf_scores.get(chunk,0)+(1/(60+rank+1))

        #5. add vector scores to dict# vector_results['document'][0] is a list of chunk texts
        for rank,chunk in enumerate(vector_results['documents'][0]):
            rrf_scores[chunk]=rrf_scores.get(chunk,0)+(1/(60+rank+1))

        sorted_rrf = sorted(rrf_scores.items(),key=lambda x:x[1],reverse=True)

        #7. return top N
        return sorted_rrf[:top_n]