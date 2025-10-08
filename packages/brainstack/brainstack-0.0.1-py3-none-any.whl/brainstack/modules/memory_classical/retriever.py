import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.preprocessing import normalize
from typing import List, Dict, Optional
from brainstack.modules.embeddings.text_embedder import TextEmbedder

class Retriever:
    """Classical text retriever using BM25 followed by cosine reranking."""
    
    def __init__(self, embedder: TextEmbedder, k: int = 5):
        """Initialize retriever with a fitted embedder and top-k limit.

        Args:
            embedder: Fitted TextEmbedder for cosine reranking.
            k: Number of results to return.
        """
        self.embedder = embedder
        self.k = k
        self.bm25: Optional[BM25Okapi] = None
        self.texts: List[str] = []
        self.ids: List[str] = []
        self.metas: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None

    def fit(self, records: List[Dict]) -> 'Retriever':
        """Build corpus index for BM25 and precompute embeddings.

        Args:
            records: List of records with 'id', 'text', 'meta' keys.

        Returns:
            Self, fitted retriever.
        """
        if not self.embedder.is_fitted:
            raise ValueError("TextEmbedder must be fitted before use")
        
        # Reset internal state
        self.texts = []
        self.ids = []
        self.metas = []
        
        # Filter valid records
        for record in records:
            if 'id' in record and 'text' in record and record['text'].strip():
                self.ids.append(record['id'])
                self.texts.append(record['text'])
                self.metas.append(record.get('meta', {}))
        
        if not self.texts:
            self.bm25 = None
            self.embeddings = None
            return self
        
        # Initialize BM25 with tokenized corpus (simple whitespace tokenization)
        tokenized_corpus = [text.lower().split() for text in self.texts]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        # Precompute embeddings (L2-normalized)
        self.embeddings = self.embedder.transform(self.texts)
        
        return self

    def query(self, q: str, topk: Optional[int] = None) -> Dict[str, List[Dict]]:
        """Retrieve top-k documents for a query using BM25 and cosine reranking.

        Args:
            q: Query string.
            topk: Number of results to return; defaults to self.k.

        Returns:
            Dict with 'hits' key containing list of result dicts:
                {'id': str, 'text': str, 'meta': dict, 'bm25': float, 'cosine': float, 'score': float}
        """
        if not q.strip() or self.bm25 is None or self.embeddings is None:
            return {"hits": []}
        
        topk = topk or self.k
        if topk <= 0:
            return {"hits": []}
        
        # Get BM25 scores for top-k*3 candidates
        tokenized_query = q.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        candidate_indices = np.argsort(bm25_scores)[::-1][:topk * 3]
        
        if not len(candidate_indices):
            return {"hits": []}
        
        # Compute query embedding
        query_embedding = self.embedder.embed(q)["vector"]
        
        # Compute cosine similarities for candidates
        candidate_embeddings = self.embeddings[candidate_indices]
        cosine_scores = np.dot(candidate_embeddings, query_embedding.T).flatten()
        
        # Normalize scores (min-max)
        bm25_subset = bm25_scores[candidate_indices]
        bm25_norm = (bm25_subset - bm25_subset.min()) / (bm25_subset.max() - bm25_subset.min() + 1e-10)
        cosine_norm = (cosine_scores - cosine_scores.min()) / (cosine_scores.max() - cosine_scores.min() + 1e-10)
        
        # Combine scores (0.5*bm25_norm + 0.5*cosine_norm)
        combined_scores = 0.5 * bm25_norm + 0.5 * cosine_norm
        sorted_indices = np.argsort(combined_scores)[::-1][:topk]
        
        # Build results
        hits = []
        for idx in sorted_indices:
            orig_idx = candidate_indices[idx]
            hits.append({
                "id": self.ids[orig_idx],
                "text": self.texts[orig_idx],
                "meta": self.metas[orig_idx],
                "bm25": float(bm25_scores[orig_idx]),
                "cosine": float(cosine_scores[idx]),
                "score": float(combined_scores[idx])
            })
        
        return {"hits": hits}

if __name__ == "__main__":
    # Test Retriever
    from brainstack.modules.embeddings.text_embedder import TextEmbedder
    
    # Create a small corpus
    corpus = [
        {"id": "1", "text": "The cat sat on the mat.", "meta": {"source": "doc1"}},
        {"id": "2", "text": "Dogs run in the park.", "meta": {"source": "doc2"}},
        {"id": "3", "text": "A cat chased a mouse.", "meta": {"source": "doc3"}}
    ]
    
    # Initialize and fit embedder
    embedder = TextEmbedder(max_features=100)
    embedder.fit([r["text"] for r in corpus])
    
    # Initialize and fit retriever
    retriever = Retriever(embedder, k=2)
    retriever.fit(corpus)
    
    # Run a query
    result = retriever.query("cat")
    print("Query: 'cat'")
    if result["hits"]:
        top_hit = result["hits"][0]
        print(f"Top hit ID: {top_hit['id']}")
        print(f"Scores: BM25={top_hit['bm25']:.3f}, Cosine={top_hit['cosine']:.3f}, Combined={top_hit['score']:.3f}")
    else:
        print("No hits found")