
import ast
import os
from collections import defaultdict

def get_imports(file_path):
    """Parse python file and return list of imported modules."""
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports

def find_cycles(root_dir):
    """Find circular dependencies in python files within root_dir."""
    dependencies = defaultdict(set)
    file_map = {}

    # Build dependency graph
    for root, dirnames, filenames in os.walk(root_dir):
        if 'tests' in root or '__pycache__' in root:
            continue
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(root, filename)
                module_name = os.path.relpath(file_path, root_dir).replace('/', '.').replace('.py', '')
                if module_name.endswith('.__init__'):
                    module_name = module_name[:-9]
                
                file_map[module_name] = file_path
                current_imports = get_imports(file_path)
                
                for imp in current_imports:
                    # Filter only internal imports
                    if imp.split('.')[0] in ['core', 'tools', 'agents', 'dashboard']:
                        dependencies[module_name].add(imp)

    # Detect cycles (DFS)
    visited = set()
    recursion_stack = set()
    cycles = []

    def dfs(node, path):
        visited.add(node)
        recursion_stack.add(node)
        
        if node in dependencies:
            for neighbor in dependencies[node]:
                # Handle relative imports or specific classes/functions
                # Approximate matching for submodules
                real_neighbor = None
                for known_mod in file_map:
                    if neighbor.startswith(known_mod):
                        real_neighbor = known_mod
                        break
                
                if not real_neighbor:
                    continue
                    
                if real_neighbor not in visited:
                    dfs(real_neighbor, path + [real_neighbor])
                elif real_neighbor in recursion_stack:
                    cycles.append(path + [real_neighbor])

        recursion_stack.remove(node)

    for node in list(dependencies.keys()):
        if node not in visited:
            dfs(node, [node])

    return cycles

if __name__ == '__main__':
    root = "/media/juan/DATA/vertice-cyber"
    print(f"Scanning {root} for circular imports...")
    cycles = find_cycles(root)
    
    if cycles:
        print(f"⚠️ Found {len(cycles)} potential circular dependencies:")
        unique_cycles = set()
        for cycle in cycles:
            # Normalize cycle to avoid duplicates (A->B->A is same as B->A->B)
            sorted_cycle = tuple(sorted(cycle)) 
            # Actually, standard cycle print:
            cycle_str = " -> ".join(cycle)
            if cycle_str not in unique_cycles:
                 print(f"  - {cycle_str}")
                 unique_cycles.add(cycle_str)
    else:
        print("✅ No circular imports found.")
