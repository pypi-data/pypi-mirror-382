import os, json
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from joblib import Parallel, delayed
from tqdm import tqdm
import numpy as np
from .utils import file_sha256

class EmbeddingEngine:
    def __init__(self, model_name: str, cache_dir: Optional[str] = None, n_jobs: int = -1, verbose: bool = False):
        self.model = SentenceTransformer(model_name)
        self.cache_dir = cache_dir
        self.n_jobs = n_jobs
        self.verbose = verbose
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)

    def _cache_path(self, file_path: str, code_hash: str) -> str:
        safe = file_path.replace(os.sep, "__").replace(":", "_")
        return os.path.join(self.cache_dir, f"{safe}.{code_hash}.npy")

    def encode_snippets(self, snippets: List[Dict]) -> np.ndarray:
        texts = [s["code"] for s in snippets]

        if self.cache_dir:
            def enc_one(i):
                s = snippets[i]
                base_id = f"{s['file']}::{s['lines'][0]}-{s['lines'][1]}"
                code_hash = file_sha256(s["file"])[:16]
                cpath = self._cache_path(base_id, code_hash)
                if os.path.exists(cpath):
                    return np.load(cpath)
                vec = self.model.encode(texts[i], convert_to_numpy=True)
                np.save(cpath, vec)
                return vec

            it = range(len(snippets))
            if self.verbose:
                it = tqdm(it, desc="Embeddings (cached)")
            vectors = Parallel(n_jobs=self.n_jobs)(delayed(enc_one)(i) for i in it)
            return np.vstack(vectors)

        vectors = self.model.encode(texts, show_progress_bar=self.verbose, convert_to_numpy=True)
        return np.array(vectors)
