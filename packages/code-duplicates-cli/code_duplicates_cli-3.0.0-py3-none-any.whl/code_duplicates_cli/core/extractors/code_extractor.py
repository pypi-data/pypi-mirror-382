from typing import List, Dict

def extract_nodes(code: str, tree, language_name: str, min_lines: int = 0) -> List[Dict]:
    """Return list of dicts: name, type, code, start_line, end_line"""
    
    result = []
    root = tree.root_node

    FUNCTION_NODES = {
        "function_definition",      # py
        "method_definition",        # js/ts/tsx
        "function_declaration",     # js/ts
        "lexical_declaration",      # for arrow funcs var foo = () => {}
        "arrow_function",           # ts/js
        "generator_function",       # js
        "function_item",            # rust
        "func_literal",             # go (literals)
        "short_function_definition" # go
    }
    CLASS_NODES = {
        "class_definition",         # py
        "class_declaration",        # js/ts/tsx
        "type_spec"                 # go: type MyStruct struct{}
    }

    def extract_text(node):
        return code[node.start_byte:node.end_byte]

    def try_name(node):
        for child in node.children:
            if child.type in ("identifier", "name"):
                try:
                    return child.text.decode("utf8")
                except Exception:
                    return "<anonymous>"
        # for assignment-based/arrow functions
        # e.g., const foo = () => {}
        if node.type in ("lexical_declaration",) and node.children:
            # look for identifier before '='
            for ch in node.children:
                if ch.type == "variable_declarator":
                    for g in ch.children:
                        if g.type == "identifier":
                            try:
                                return g.text.decode("utf8")
                            except Exception:
                                return "<anonymous>"
        return "<anonymous>"

    def walk_tree(node):
        if node.type in FUNCTION_NODES:
            name = try_name(node)
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            if (end_line - start_line + 1) >= min_lines:
                result.append({
                    "name": name,
                    "type": "function",
                    "code": extract_text(node),
                    "start_line": start_line,
                    "end_line": end_line
                })
        
        elif node.type in CLASS_NODES:
            name = try_name(node)
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            if (end_line - start_line + 1) >= min_lines:
                result.append({
                    "name": name,
                    "type": "class",
                    "code": extract_text(node),
                    "start_line": start_line,
                    "end_line": end_line
                })

        for child in node.children:
            walk_tree(child)

    walk_tree(root)
    return result
