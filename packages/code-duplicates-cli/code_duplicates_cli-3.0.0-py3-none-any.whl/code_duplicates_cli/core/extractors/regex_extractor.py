import re
from typing import List, Dict

class RegexExtractor:
    """Regex-based function extractor as fallback when tree-sitter fails"""
    
    def __init__(self, language: str):
        self.language = language
        self.patterns = self._get_patterns(language)
    
    def _get_patterns(self, language: str) -> Dict:
        """Get regex patterns for different languages"""
        patterns = {
            'python': {
                'function': r'^(\s*)(def\s+(\w+)\s*\([^)]*\)\s*:.*?)(?=^\1\S|\Z)',
                'class': r'^(\s*)(class\s+(\w+).*?:.*?)(?=^\1\S|\Z)',
            },
            'javascript': {
                'function': r'(function\s+(\w+)\s*\([^)]*\)\s*\{[^}]*\})',
                'arrow_function': r'((?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{[^}]*\})',
                'method': r'(\s*(\w+)\s*\([^)]*\)\s*\{[^}]*\})',
            },
            'typescript': {
                'function': r'(function\s+(\w+)\s*\([^)]*\)\s*:?\s*[^{]*\{[^}]*\})',
                'arrow_function': r'((?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*:?\s*[^=]*=>\s*\{[^}]*\})',
                'method': r'(\s*(\w+)\s*\([^)]*\)\s*:?\s*[^{]*\{[^}]*\})',
            }
        }
        
        if language in ['jsx', 'tsx']:
            return patterns.get('javascript', {})
        
        return patterns.get(language, {})
    
    def extract_functions(self, code: str, min_lines: int = 0) -> List[Dict]:
        """Extract functions using regex patterns"""
        functions = []
        
        if not self.patterns:
            return functions
        
        lines = code.split('\n')
        
        for pattern_name, pattern in self.patterns.items():
            if self.language == 'python':
                matches = re.finditer(pattern, code, re.MULTILINE | re.DOTALL)
            else:
                matches = re.finditer(pattern, code, re.MULTILINE)
            
            for match in matches:
                function_code = match.group(1) if len(match.groups()) >= 1 else match.group(0)
                function_name = match.group(3) if len(match.groups()) >= 3 else match.group(2) if len(match.groups()) >= 2 else "anonymous"
                
                start_pos = match.start()
                end_pos = match.end()
                
                start_line = code[:start_pos].count('\n')
                end_line = code[:end_pos].count('\n')
                
                if (end_line - start_line + 1) >= min_lines:
                    functions.append({
                        'name': function_name,
                        'type': 'class' if 'class' in pattern_name else 'function',
                        'code': function_code.strip(),
                        'start_line': start_line,
                        'end_line': end_line,
                    })
        
        return functions

class MockTree:
    """Mock tree object to maintain compatibility with existing code"""
    def __init__(self, functions: List[Dict]):
        self.functions = functions
        self.root_node = MockNode()

class MockNode:
    """Mock node to maintain compatibility"""
    def __init__(self):
        pass