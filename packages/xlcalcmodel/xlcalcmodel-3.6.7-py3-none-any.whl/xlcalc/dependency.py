##dependency.py

import re
import time
from xlcalc.references import CellAddress
from xlcalc.parser import RangeNode
from collections import defaultdict, deque

def topologically_sort_subgraph(dependency_graph, subgraph_nodes):
    """
    Attempt to return a topologically sorted list of nodes from subgraph_nodes,
    such that for each cell A in the list, every cell that A depends on (that is
    also in subgraph_nodes) appears before A.
    
    If the subgraph has cycles, this algorithm returns a partial order for the
    acyclic portion.
    """
    # Compute in-degree for nodes in the subgraph.
    in_degree = {node: 0 for node in subgraph_nodes}
    for node in subgraph_nodes:
        # For each dependency of node that is also in the subgraph, add to its in-degree.
        for dep in dependency_graph.get(node, []):
            if dep in subgraph_nodes:
                in_degree[node] += 1

    # Start with all nodes that have no incoming edges.
    queue = deque([node for node, deg in in_degree.items() if deg == 0])
    sorted_order = []

    while queue:
        node = queue.popleft()
        sorted_order.append(node)
        # For every other node in the subgraph,
        # if 'node' is a dependency of that node, decrement its in-degree.
        for other in subgraph_nodes:
            if node in dependency_graph.get(other, []):
                in_degree[other] -= 1
                if in_degree[other] == 0:
                    queue.append(other)
    return sorted_order

def subgraph_has_cycle(model, subgraph_nodes):
    """
    Return True if there is any circular reference in the given subgraph
    (i.e. if any node can reach itself by following dependencies).
    """
    adjacency = model.dependency_graph  # cell -> list of cells it depends on
    visited = set()
    rec_stack = set()  # keeps track of nodes in the current DFS path

    def dfs(cell):
        visited.add(cell)
        rec_stack.add(cell)
        for dep in adjacency.get(cell, []):
            # Only follow edges within the relevant subgraph
            if dep in subgraph_nodes:
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    return True
        rec_stack.remove(cell)
        return False

    # Run DFS from each node in subgraph (unless already visited)
    for node in subgraph_nodes:
        if node not in visited:
            if dfs(node):
                return True
    return False

def build_reverse_dependency_graph(model):
    """Return a mapping of each cell to the list of cells that depend on it."""
    reverse = defaultdict(list)
    for cell, deps in model.dependency_graph.items():
        for dep in deps:
            reverse[dep].append(cell)
    return reverse

def find_cycle_nodes(model, subgraph_nodes):
    """Return the subset of nodes that are part of a dependency cycle."""
    adjacency = model.dependency_graph
    index = 0
    stack = []
    indices = {}
    lowlink = {}
    on_stack = set()
    cycles = set()

    def strongconnect(v):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)
        for w in adjacency.get(v, []):
            if w not in subgraph_nodes:
                continue
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])
        if lowlink[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == v:
                    break
            if len(scc) > 1:
                cycles.update(scc)
            else:
                # single node SCC => check self-loop
                if v in adjacency.get(v, []):
                    cycles.add(v)

    for node in subgraph_nodes:
        if node not in indices:
            strongconnect(node)

    return cycles

def get_full_dependency_chain(model, start_canonical, visited=None):
    """Recursively build a set of all cells (canonical addresses) that contribute to start_canonical."""
    if visited is None:
        visited = set()
    if start_canonical in visited:
        return visited
    visited.add(start_canonical)
    # Look up the dependencies in the prebuilt dependency graph.
    deps = model.dependency_graph.get(start_canonical, [])
    for dep in deps:
        get_full_dependency_chain(model, dep, visited)
    return visited

def extract_references_from_ast(ast_node, model, default_sheet, visited=None):
    """
    Recursively gather normalized canonical addresses that the given AST node
    depends on. Normalizes addresses by removing '$' characters.
    """
    from xlcalc.parser import RangeNode, FunctionNode
    from xlcalc.references import CellAddress

    if visited is None:
        visited = set()
    if id(ast_node) in visited:
        return set()
    visited.add(id(ast_node))

    refs = set()

    # --- 1) If ast_node is a RangeNode (e.g. "Sheet1!A1:C1") ---
    if isinstance(ast_node, RangeNode):
        rng_str = ast_node.tvalue
        if '!' in rng_str:
            sheet_part, rng_part = rng_str.split('!', 1)
            sheet_name = sheet_part.strip().strip("'")
        else:
            sheet_name = default_sheet
            rng_part = rng_str

        if ':' in rng_part:
            # Multi-cell range: expand it via model.resolve_range
            addr_objs = model.resolve_range(sheet_name, rng_part)
            for addr in addr_objs:
                refs.add(addr.canonical_address().replace('$', ''))
        else:
            # Single-cell range: parse it directly
            addr_obj = CellAddress.from_string(rng_part)
            if not addr_obj.sheet:
                addr_obj.sheet = sheet_name
            refs.add(addr_obj.canonical_address().replace('$', ''))
              
        # Also recurse into any child nodes (e.g. for compound ranges)
        for attr in ['left', 'right']:
            child = getattr(ast_node, attr, None)
            if child is not None:
                refs |= extract_references_from_ast(child, model, default_sheet, visited)
        if hasattr(ast_node, 'args') and ast_node.args:
            for child in ast_node.args:
                refs |= extract_references_from_ast(child, model, default_sheet, visited)
        return refs

    # --- 2) If it's a single-cell REF or RANGE token (like "A1" or "Sheet!A1") ---
    if hasattr(ast_node, 'token') and getattr(ast_node.token, 'ttype', None) in {"REF", "RANGE"}:
        try:
            token_value = ast_node.token.tvalue.strip()
            addr_obj = CellAddress.from_string(token_value)
            if not addr_obj.sheet and default_sheet:
                addr_obj.sheet = default_sheet
            refs.add(addr_obj.canonical_address().replace('$', ''))
        except Exception:
            pass
        return refs

    # --- 3) If it's a FunctionNode, process its arguments explicitly ---
    if isinstance(ast_node, FunctionNode):
        for argnode in ast_node.args:
            refs |= extract_references_from_ast(argnode, model, default_sheet, visited)
        # Optionally also check left/right children if they exist:
        for attr in ['left', 'right']:
            child = getattr(ast_node, attr, None)
            if child is not None:
                refs |= extract_references_from_ast(child, model, default_sheet, visited)
        return refs

    # --- 4) Otherwise, recursively check .left, .right, and .args ---
    for attr in ['left', 'right']:
        child = getattr(ast_node, attr, None)
        if child is not None:
            refs |= extract_references_from_ast(child, model, default_sheet, visited)
    if hasattr(ast_node, 'args') and ast_node.args:
        for child in ast_node.args:
            refs |= extract_references_from_ast(child, model, default_sheet, visited)

    return refs

def build_forward_dep_chain_for_cell(model, start_canonical, visited=None, adjacency=None):
    """
    For the given cell, parse out all references. Then recursively build
    the chain for each reference. The result is adjacency dict:
       adjacency[ CellA ] = [dep1, dep2, ...]
    meaning "CellA depends on dep1, dep2, etc."

    This routine automatically handles cross-sheet references as long
    as the formula includes an explicit sheet, e.g. =Sheet1!A1.
    """
    if visited is None:
        visited = set()
    if adjacency is None:
        adjacency = defaultdict(list)

    if start_canonical in visited:
        return adjacency

    visited.add(start_canonical)

    cell = model.get_cell_by_canonical_address(start_canonical)
    if not cell:
        # e.g. references a nonexistent cell? do nothing
        return adjacency

    if cell.formula and cell.parsed_ast:
        # Find direct references from this cell's formula
        refs = extract_references_from_ast(cell.parsed_ast, model,
                                           default_sheet=cell.address_obj.sheet)
        # For each reference, store adjacency and recurse
        for ref_canonical in refs:
            adjacency[start_canonical].append(ref_canonical)
            build_forward_dep_chain_for_cell(model, ref_canonical, visited, adjacency)

    return adjacency
