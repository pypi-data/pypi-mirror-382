import re
from typing import List, Dict

def extract_functions_simple(code: str, language: str, min_lines: int = 0) -> List[Dict]:
    """Simple regex-based function extractor"""
    functions = []
    
    if language == "python":
        pattern = r'^(\s*)(def\s+(\w+)\s*\([^)]*\)\s*:.*?)(?=^\1\S|\Z)'
        matches = re.finditer(pattern, code, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            function_code = match.group(2)
            function_name = match.group(3)
            
            start_pos = match.start(2)
            end_pos = match.end(2)
            start_line = code[:start_pos].count('\n')
            end_line = code[:end_pos].count('\n')
            
            if (end_line - start_line + 1) >= min_lines:
                functions.append({
                    'name': function_name,
                    'type': 'function',
                    'code': function_code.strip(),
                    'start_line': start_line,
                    'end_line': end_line,
                })
    
    elif language in ["javascript", "typescript"]:
        patterns = [
            r'function\s+(\w+)\s*\([^)]*\)\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # function declarations
            r'(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # arrow functions
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, code, re.MULTILINE)
            
            for match in matches:
                function_code = match.group(0)
                function_name = match.group(1)
                
                start_pos = match.start()
                end_pos = match.end()
                start_line = code[:start_pos].count('\n')
                end_line = code[:end_pos].count('\n')
                
                if (end_line - start_line + 1) >= min_lines:
                    functions.append({
                        'name': function_name,
                        'type': 'function',
                        'code': function_code.strip(),
                        'start_line': start_line,
                        'end_line': end_line,
                    })
    
    return functions

class MockTree:
    """Mock tree object to maintain compatibility"""
    def __init__(self, functions: List[Dict]):
        self.functions = functions
        self.root_node = MockNode()

class MockNode:
    """Mock node to maintain compatibility"""
    def __init__(self):
        pass