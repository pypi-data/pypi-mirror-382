import faiss
import numpy as np
from typing import List, Dict

class SimilarityEngine:
    def __init__(self, threshold: float = 0.9, top_k: int = 5):
        self.threshold = threshold
        self.top_k = top_k

    def find_duplicates(self, vectors: np.ndarray, snippets: List[Dict]):
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(vectors)
        index.add(vectors)

        k = min(self.top_k + 1, len(snippets))
        sims, idxs = index.search(vectors, k)

        duplicates = []
        seen_pairs = set()

        for i, (sim_row, idx_row) in enumerate(zip(sims, idxs)):
            for sim, j in zip(sim_row, idx_row):
                if i == j:
                    continue
                    
                if sim >= self.threshold:
                    a = snippets[i]
                    b = snippets[j]
                    
                    if (a["file"] == b["file"] and 
                        a["lines"] == b["lines"] and 
                        a["symbol"] == b["symbol"]):
                        continue
                    
                    key = tuple(sorted([ (a["file"], a["lines"]), (b["file"], b["lines"]) ]))
                    if key in seen_pairs:
                        continue
                    seen_pairs.add(key)
                    duplicates.append({
                        "a": a,
                        "b": b,
                        "similarity": float(sim)
                    })
        duplicates.sort(key=lambda d: d["similarity"], reverse=True)
        return duplicates
