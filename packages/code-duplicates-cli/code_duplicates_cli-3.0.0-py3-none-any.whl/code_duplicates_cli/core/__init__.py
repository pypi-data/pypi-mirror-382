"""Core modules for code duplicate detection."""

from .config import *
from .embeddings import EmbeddingEngine
from .similarity import SimilarityEngine
from .report import generate_reports
from .utils import scan_files

__all__ = [
    "EmbeddingEngine",
    "SimilarityEngine", 
    "generate_reports",
    "scan_files",
]