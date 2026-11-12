from rank_bm25 import BM25Okapi

class BM25Search:
    def __init__(self, chunks: list[str]):
        self.chunks = chunks
        # 1. Tokenize: lowercase and split into words
        tokenized_corpus = [doc.lower().split() for doc in chunks]
        # 2. Build the BM25 index
        self.bm25 = BM25Okapi(tokenized_corpus)
        
    def search(self, query: str, top_n: int = 2):
        # 1. Tokenize the query the exact same way
        tokenized_query = query.lower().split()
        
        # 2. Get a list of scores for every chunk
        scores = self.bm25.get_scores(tokenized_query)
        
        # 3. Pair the scores with the chunks and sort them highest to lowest
        # zip() combines (score, chunk) into a tuple
        scored_chunks = list(zip(scores, self.chunks))
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # 4. Return the top N results
        return scored_chunks[:top_n]