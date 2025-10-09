# incremental_calculator.py

from xlcalc.dependency import (
    subgraph_has_cycle,
    get_full_dependency_chain,
    topologically_sort_subgraph,
    build_forward_dep_chain_for_cell,
    build_reverse_dependency_graph,
    find_cycle_nodes,
)
from .xltypes import XlReference
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

def iterative_target_cell(ctx, target_canonical):
    model = ctx.model
    target_cell = model.get_cell_by_canonical_address(target_canonical)

    # Gather the subgraph: all cells that contribute to target, plus target.
    subgraph_nodes = get_upstream_cells(model, target_canonical)
    subgraph_nodes.add(target_canonical)

    cycle_nodes = find_cycle_nodes(model, subgraph_nodes)
    affected_nodes = get_dependents_for_nodes(model, cycle_nodes)
    affected_nodes.update(cycle_nodes)
    affected_nodes.add(target_canonical)
    
    old_val = target_cell.value if isinstance(target_cell.value, (int, float)) else 0.0
    
    # First iteration recalculates entire subgraph
    for addr in subgraph_nodes:
        cobj = model.get_cell_by_canonical_address(addr)
        if cobj and cobj.formula:
            cobj.need_update = True
            
    ctx._cache.clear()
    
    new_val = ctx.eval_cell_value(target_cell)
    logger.debug(f"ITER 1 old_val={old_val}, new_val={new_val}")
    if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
        delta = abs(new_val - old_val)
        if delta <= ctx.max_change:
            return target_cell.value
        old_val = new_val
    else:
        old_val = new_val

    for iteration in range(1, ctx.max_iterations):
        for addr in affected_nodes:
            cobj = model.get_cell_by_canonical_address(addr)
            if cobj and cobj.formula:
                cobj.need_update = True
            ctx._cache.pop(addr, None)

        new_val = ctx.eval_cell_value(target_cell)

        #print(f"ITER {iteration+1} old_val={old_val}, new_val={new_val}")
        logger.debug(f"ITER {iteration+1} old_val={old_val}, new_val={new_val}")
        
        # 4) If numeric, measure delta
        if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
            delta = abs(new_val - old_val)
            if delta <= ctx.max_change:
                #print(f"Converged after {iteration+1} iterations, delta={delta}")
                logger.debug(f"Converged after {iteration+1} iterations, delta={delta}")
                break
            old_val = new_val
        else:
            # If not numeric, e.g. string result, just do fixed passes or break
            old_val = new_val

    return target_cell.value

def recalc_or_iterate(ctx, target_canonical):
    """
    Automatically do a single-pass recalculation if no circular reference is
    found in the target's subgraph. If a cycle is detected, do iterative passes
    on that subgraph until convergence.
    """
    model = ctx.model
    # Build the subgraph: all upstream cells plus the target itself
    subgraph = get_upstream_cells(model, target_canonical)
    subgraph.add(target_canonical)

    # If any cell in subgraph is part of a circular loop, do iterative calc:
    if subgraph_has_cycle(model, subgraph):
        return iterative_target_cell(ctx, target_canonical)
    else:
        return recalc_target_cell(ctx, target_canonical)
    
def get_dependent_cells(model, start_cell_canonical):
    """
    Given a starting cell canonical address (e.g., "Sheet1!A1"),
    return the set of cells (canonical addresses) that depend on it, transitively.
    """
    reverse_graph = model.reverse_dependency_graph
    affected = set()
    stack = [start_cell_canonical]
    while stack:
        current = stack.pop()
        if current in affected:
            continue
        affected.add(current)
        for dependent in reverse_graph.get(current, []):
            stack.append(dependent)
    return affected

def get_dependents_for_nodes(model, nodes):
    """Return all cells that depend on any of the given nodes."""
    reverse_graph = model.reverse_dependency_graph
    affected = set()
    stack = list(nodes)
    while stack:
        current = stack.pop()
        if current in affected:
            continue
        affected.add(current)
        for dependent in reverse_graph.get(current, []):
            stack.append(dependent)
    return affected

def recalc_target_cell(ctx, target_canonical):
    target_cell = ctx.model.get_cell_by_canonical_address(target_canonical)
    if target_cell is None:
        raise ValueError(f"Target cell {target_canonical} not found.")
    
    # Clear any cached values to force a fresh evaluation.
    ctx._cache.clear()

    # Finally, re-evaluate and return the cell's value.
    return ctx.eval_cell_value(target_cell)

def mark_upstream_chain_dirty(model, target_cell_canonical):
    """
    Mark every cell that feeds into 'target_cell_canonical' as dirty
    by setting cell.need_update = True, so they will be recalculated.
    
    This also ensures the target cell itself is included and
    prints debug info confirming each cell's need_update status.
    """
    upstream_cells = get_upstream_cells(model, target_cell_canonical)
    upstream_cells.add(target_cell_canonical)

    # Now mark them all dirty and print debug info.
    for canonical in upstream_cells:
        cell = model.get_cell_by_canonical_address(canonical)
        if cell and cell.formula:
            cell.need_update = True
##            #print(f"[DEBUG] Marking '{canonical}' dirty => need_update=True")

    #print("[DEBUG] Final list of cells marked dirty:")
    for canonical in sorted(upstream_cells):
        cell_obj = model.get_cell_by_canonical_address(canonical)
##        if cell_obj:
##            #print(f"   {canonical} => need_update={cell_obj.need_update}, value={cell_obj.value}")
##        else:
##            #print(f"   {canonical} => (no cell found in model)")

    return upstream_cells

def get_upstream_cells(model, start_cell_canonical):
    """
    Return a set of all cells (canonical addresses) that feed into
    start_cell_canonical, including the start cell itself.
    """

    # Lazily initialize cache on the model
    cache = getattr(model, "upstream_cache", None)
    if cache is None:
        cache = model.upstream_cache = {}

    if start_cell_canonical in cache:
        return cache[start_cell_canonical]
    
    visited = set()
    stack = [start_cell_canonical]

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        # Each entry in 'dependency_graph[current]' is a canonical address
        # that 'current' depends on. So that's 'upstream'.
        for upstream in model.dependency_graph.get(current, []):
            if upstream not in visited:
                if upstream in cache:
                    visited.update(cache[upstream])
                else:
                    stack.append(upstream)

    cache[start_cell_canonical] = visited
    return visited
