import tree_sitter
from typing import Optional

try:
    import tree_sitter_python as ts_python
    PYTHON_AVAILABLE = True
except ImportError:
    ts_python = None
    PYTHON_AVAILABLE = False

try:
    import tree_sitter_javascript as ts_javascript
    JAVASCRIPT_AVAILABLE = True
except ImportError:
    ts_javascript = None
    JAVASCRIPT_AVAILABLE = False

SUPPORTED_LANGUAGES = {
    "py": ("python", ts_python, PYTHON_AVAILABLE),
    "js": ("javascript", ts_javascript, JAVASCRIPT_AVAILABLE),
    "jsx": ("javascript", ts_javascript, JAVASCRIPT_AVAILABLE),
}

class ParserManager:
    def __init__(self, lang_ext: str):
        if lang_ext not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language not supported: {lang_ext}")
        
        lang_name, lang_module, available = SUPPORTED_LANGUAGES[lang_ext]
        
        if not available:
            raise RuntimeError(f"Tree-sitter parser for {lang_name} is not available. Please install tree-sitter-{lang_name}")
        
        self.lang_name = lang_name
        self.original_ext = lang_ext
        
        try:
            if hasattr(lang_module, 'language'):
                language_obj = lang_module.language()
            else:
                raise AttributeError(f"Module {lang_module} does not have a 'language' function")
                
            self.language = tree_sitter.Language(language_obj)
            self.parser = tree_sitter.Parser(self.language)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize {lang_name} parser: {e}")

    def parse(self, code: str):
        """Parse code and return tree"""
        try:
            return self.parser.parse(bytes(code, "utf8"))
        except Exception as e:
            raise RuntimeError(f"Failed to parse code with {self.lang_name} parser: {e}")
