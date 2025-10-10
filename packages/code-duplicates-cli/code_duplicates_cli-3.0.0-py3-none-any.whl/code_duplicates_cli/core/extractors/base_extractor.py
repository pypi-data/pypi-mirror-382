import os
from typing import List, Dict
from .parser_manager import ParserManager
from .code_extractor import extract_nodes

def extract_functions(files: List[str], languages: List[str] = None, min_lines: int = 0) -> List[Dict]:
    snippets = []
    for file in files:
        ext = os.path.splitext(file)[1].replace(".", "").lower()
        
        if languages and ext not in languages:
            continue
            
        try:
            parser = ParserManager(ext)
        except ValueError as e:
            continue
        except Exception as e:
            print(f"⚠️ Error creating parser for {ext} in {file}: {e}")
            continue
        try:
            with open(file, "r", encoding="utf8") as f:
                code = f.read()
            tree = parser.parse(code)
            nodes = extract_nodes(code, tree, parser.lang_name, min_lines=min_lines)
            for n in nodes:
                snippets.append({
                    "file": file,
                    "language": parser.lang_name,
                    "symbol": n["name"],
                    "type": n["type"],
                    "code": n["code"],
                    "lines": (n["start_line"], n["end_line"]),
                })
        except Exception as e:
            print(f"⚠️ Error en {file}: {e}")
    return snippets
