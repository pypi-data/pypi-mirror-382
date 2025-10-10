import os, hashlib
from typing import List, Set
import fnmatch

def load_exclusions(exclusions_file: str = None) -> Set[str]:
    """Load exclusions from file or return default exclusions."""
    default_exclusions = {
        "node_modules",
        ".git",
        ".svn",
        ".hg",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        ".coverage",
        "dist",
        "build",
        ".next",
        ".nuxt",
        "target",  # Rust
        "vendor",  # Go
        ".venv",
        "venv",
        "env",
        ".env",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        "*.tmp",
        "*.temp",
        ".idea",
        ".vscode",
        "*.min.js",
        "*.min.css",
    }
    
    if exclusions_file and os.path.exists(exclusions_file):
        try:
            with open(exclusions_file, 'r', encoding='utf-8') as f:
                file_exclusions = {line.strip() for line in f if line.strip() and not line.startswith('#')}
            return default_exclusions.union(file_exclusions)
        except Exception as e:
            print(f"⚠️ Error reading exclusions file {exclusions_file}: {e}")
    
    return default_exclusions

def should_exclude(path: str, exclusions: Set[str]) -> bool:
    """Check if a path should be excluded based on exclusion patterns."""
    path_parts = path.replace('\\', '/').split('/')
    
    for exclusion in exclusions:
        for part in path_parts:
            if fnmatch.fnmatch(part, exclusion):
                return True
        
        if fnmatch.fnmatch(path.replace('\\', '/'), exclusion):
            return True
    
    return False

def scan_files(path: str, languages: List[str], exclusions_file: str = None):
    exclusions = load_exclusions(exclusions_file)
    matches = []
    
    for root, dirs, files in os.walk(path):
        rel_root = os.path.relpath(root, path)
        
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(rel_root, d), exclusions)]
        
        for f in files:
            file_path = os.path.join(root, f)
            rel_file_path = os.path.relpath(file_path, path)
            
            if should_exclude(rel_file_path, exclusions):
                continue
                
            ext = f.split(".")[-1].lower()
            if ext in languages:
                matches.append(file_path)
    
    return matches

def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
