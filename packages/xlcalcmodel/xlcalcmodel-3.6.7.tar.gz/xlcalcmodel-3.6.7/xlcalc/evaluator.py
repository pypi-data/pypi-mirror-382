## evaluator.py

import logging
import numpy as np
from .parser import FormulaParser
from .funcs.xl import FUNCTIONS  # global function registry
from .xltypes import XlReference, XlArray
from xlcalc.funcs.func_xltypes import Array

logger = logging.getLogger(__name__)

def flatten_array(val):
    """
    Flatten scalars or nested lists/tuples (or XlArray objects) into a single list of values.
    If the value is a string that might represent a number (even with commas),
    try to convert it to a float; if conversion fails, return the original.
    """
    logger.debug("flatten_array: called with val=%r", val)
    # Import here to avoid circular dependency issues.
    from .xltypes import XlArray

    # If the value is an XlArray, convert its data (a numpy array) to a list.
    if isinstance(val, XlArray):
        return flatten_array(val.data.tolist())

    # Also treat tuples like lists.
    if not isinstance(val, (list, tuple)):
        if isinstance(val, str):
            cleaned = val.replace(',', '')
            logger.debug("flatten_array: cleaned string from %r to %r", val, cleaned)
            try:
                result = float(cleaned)
                logger.debug("flatten_array: converted cleaned string %r to float: %r", cleaned, result)
                return [result]
            except ValueError as e:
                logger.debug("flatten_array: conversion failed for string %r: %s", cleaned, e)
                return [val]
        else:
            try:
                result = float(val)
                logger.debug("flatten_array: converted %r to float: %r", val, result)
                return [result]
            except (ValueError, TypeError) as e:
                logger.debug("flatten_array: conversion failed for %r: %s", val, e)
                return [val]
    else:
        out = []
        logger.debug("flatten_array: processing list/tuple %r", val)
        for item in val:
            flattened = flatten_array(item)
            logger.debug("flatten_array: flattened item %r to %r", item, flattened)
            out.extend(flattened)
        logger.debug("flatten_array: final flattened result: %r", out)
        return out

class EvalContext:
    def __init__(self, model, sheet="Sheet1", iterative=False, max_iterations=100, max_change=0.001):
        """
        Create an evaluation context.
        
        Parameters:
            model          : The workbook model.
            sheet          : Default sheet name.
            iterative      : If True, enables Excel-like iterative calculation.
            max_iterations : Maximum iterations for convergence.
            max_change     : Convergence tolerance.
        """
        self.model = model
        self.sheet = sheet
        self._cache = {}            # Cache: cell reference -> computed value
        self._evaluation_stack = [] # Used for cycle detection
        self.parser = FormulaParser()  # Parser instance
        self.current_function = None   # For function calls

        # Iterative calculation parameters:
        self.iterative = iterative
        self.max_iterations = max_iterations
        self.max_change = max_change
        self.old_values = {}  # Initialize old_values to an empty dict

    def eval_cell_value(self, cell, bypass_cycle_detection=False):
        if cell is None:
            #print("eval_cell_value: cell is None, returning 0.0")
            logger.debug("eval_cell_value: cell is None, returning 0.0")
            return 0.0

        cell_ref = cell.address_obj.canonical_address()
        #print(f" Re-eval pass for {cell_ref}, need_update={cell.need_update}, old_val={self.old_values.get(cell_ref)}, new_val={cell.value}")
        logger.debug(
            "Re-eval pass for %s, need_update=%s, old_val=%s, new_val=%s",
            cell_ref, cell.need_update, self.old_values.get(cell_ref), cell.value
        )
        #print(f"[eval_cell_value] Evaluating {cell_ref} (formula={cell.formula}, value={cell.value})")
        logger.debug(
            "[eval_cell_value] Evaluating %s (formula=%r, value=%r)",
            cell_ref, cell.formula, cell.value
        )

        # 1) Cycle detection
        if cell_ref in self._evaluation_stack:
            if not self.iterative:
                # Non-iterative => raise error for cycles
                cycle_chain = " -> ".join(self._evaluation_stack + [cell_ref])
                #print("Cycle detected:", cycle_chain)
                logger.error("Cycle detected: %s", cycle_chain)
                raise RuntimeError(f"Cycle detected in evaluation: {cycle_chain}")
            else:
                # Iterative mode => let Excel-like iteration handle it.
                # Just return whatever we have so far (cell.value or 0)
                # so we don't infinitely recurse in this pass.
                #print(f"[CYCLE] iterative mode for {cell_ref}, skipping deeper recursion this pass.")
                logger.debug(
                    "[CYCLE] iterative mode for %s, skipping deeper recursion this pass.",
                    cell_ref
                )
                #return cell.value if cell.value is not None else 0.0
                # Use the previous iteration’s value if available.
                old_val =  self.old_values.get(cell_ref, cell.value if cell.value is not None else 0.0)
                #print(f"[CYCLE] iterative mode for {cell_ref}, returning old_values[{cell_ref}] = {old_val}")
                logger.debug(
                    "[CYCLE] iterative mode for %s, returning old_values[%s] = %s",
                    cell_ref, cell_ref, old_val
                )
                return old_val

        # 2) If cell is dirty, we skip the cache.
        #    Otherwise, if it's clean, we can use the existing cached value if it exists.
        if not cell.need_update:
            # Not dirty => check cache
            if cell_ref in self._cache:
                #print(f"Cache hit for cell {cell_ref}, returning {self._cache[cell_ref]}")
                logger.debug("Cache hit for cell %s, returning %r", cell_ref, self._cache[cell_ref])
                return self._cache[cell_ref]
        else:
            #print(f"Skipping cache since {cell_ref} is dirty")
            logger.debug("Skipping cache since %s is dirty", cell_ref)

        # 3) Normal (re)calculation
        old_sheet = self.sheet
        if cell.address_obj.sheet:
            self.sheet = cell.address_obj.sheet

        self._evaluation_stack.append(cell_ref)
        try:
            # If there's no formula, treat this cell as a direct value.
            if not cell.formula:
                result = cell.value if cell.value is not None else 0.0
                cell.need_update = False
                self._cache[cell_ref] = result
                return result

            # Evaluate formula using compiled function when available
            if getattr(cell, 'compiled_func', None):
                val = cell.compiled_func(self)
            else:
                if cell.parsed_ast:
                    val = cell.parsed_ast.eval(self)
                else:
                    ast_node = self.parser.parse(cell.formula)
                    val = ast_node.eval(self)
                    cell.parsed_ast = ast_node

            # Unwrap references (in case result is XlReference or function returning references)
            while hasattr(val, "eval"):
                val = val.eval(self)
            if isinstance(val, XlReference):
                val = val.get_value(self)

            # Store final result
            cell.value = val
            cell.need_update = False         # Mark clean after this recalculation
            self._cache[cell_ref] = val      # Update the cache
            #print(f"[DEBUG] Setting old_values[{cell_ref}] = {val}")
            logger.debug("[DEBUG] Setting old_values[%s] = %r", cell_ref, val)
            self.old_values[cell_ref] = val  # Keep track for iterative logic

            return val

        finally:
            self._evaluation_stack.pop()
            self.sheet = old_sheet

    def call_function(self, name, argvals):
        current_fn_name = name.upper()  # Save the function name in a local variable.
        self.current_function = current_fn_name 
        #print("Function call:", current_fn_name, self, name, argvals)
        logger.debug("Function call: %s, %s, %s, %s", current_fn_name, self, name, argvals)
        
        # (Process arguments as before.)
        if current_fn_name in {"VLOOKUP", "HLOOKUP", "SUM", "SUMPRODUCT", "MAX", "MIN"}:
            new_args = []
            for idx, arg in enumerate(argvals):
                if isinstance(arg, XlReference):
                    val = arg.get_value(self)
                    if isinstance(val, (list, tuple)) and not hasattr(val, "data"):
                        val = Array(val)
                    new_args.append(val)
                elif isinstance(arg, (list, tuple)) and not hasattr(arg, "data"):
                    new_args.append(Array(arg))
                else:
                    new_args.append(arg)
            argvals = new_args
        else:
            if current_fn_name not in {"COLUMN", "ROW", "IF", "IFERROR", "SUMPRODUCT"}:
                argvals = [arg.get_value(self) if isinstance(arg, XlReference) else arg for arg in argvals]
    
        # Use the local variable for the lookup.
        fn = FUNCTIONS.get(current_fn_name)
        if not fn:
            logger.debug("Function '%s' not found, returning 0.0", name)
            self.current_function = None
            return 0.0
    
        if current_fn_name in {"VLOOKUP", "HLOOKUP", "COLUMN", "SUM", "IF", "IFERROR", "SUMPRODUCT", "MAX", "MIN"}:
            result = fn(*argvals, context=self)
        else:
            result = fn(*argvals)
    
        logger.debug("Function %s returned %r", current_fn_name, result)
        self.current_function = None
        return result
