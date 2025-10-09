## xltypes.py

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np

class XLType:
    """
    Base class for typed Excel-like objects (optional).
    You can expand with typed numeric, text, etc. if desired.
    """
    pass

@dataclass
class XLFormula(XLType):
    """
    Minimal wrapper for a formula string that:
      - Stores the raw formula
      - Optionally references a sheet name
      - On init, uses your parser to get tokens & AST
    """
    formula: str                   
    sheet_name: Optional[str] = None
    reference: Optional[str] = None
    evaluate: bool = True

    # We'll store the tokens/AST from your parser:
    tokens: list = field(default_factory=list, repr=False)
    ast: Optional[object] = None   # or a more specific ASTNode type

    def __post_init__(self):
        # If the formula starts with '=', strip it
        form_str = self.formula.strip()
        if form_str.startswith('='):
            form_str = form_str[1:].strip()
        
        # LOCAL IMPORT to break circular dependency:
        from .parser import FormulaParser

        # Parse with your existing parser
        parser = FormulaParser()
        parsed_ast = parser.parse(self.formula)

        # If your parser stores tokens in parser.tokens or parser.tokens2, adapt as needed
        self.tokens = getattr(parser, 'tokens', [])
        self.ast = parsed_ast

    def __repr__(self):
        return (f"<XLFormula formula='{self.formula}' "
                f"sheet_name={self.sheet_name!r} "
                f"reference={self.reference!r} "
                f"evaluate={self.evaluate!r}>")

class XlReference(XLType):
    """
    A wrapper for a cell reference that preserves the underlying CellAddress.
    This allows functions like COLUMN to extract the original reference (e.g. A$1)
    rather than its evaluated value.
    """
    def __init__(self, cell_addr):
        self.cell_addr = cell_addr  # Expected to be a CellAddress instance

    def get_address(self):
        return self.cell_addr

    def __eq__(self, other):
        if isinstance(other, XlReference):
            return self.cell_addr == other.cell_addr
        return False

    def __hash__(self):
        return hash(self.cell_addr)
        
    def get_value(self, context):
        """
        1) Resolve sheet name if missing.
        2) Retrieve cell from model.
        3) If cell.need_update, force a fresh eval via ctx.eval_cell_value.
        4) Otherwise, use the current cell.value (if it exists) or recalc as fallback.
        5) Unwrap nested XlReference instances.
        """
        if not self.cell_addr.sheet:
            self.cell_addr.sheet = context.sheet

        cell_ref = self.cell_addr.canonical_address()
        cell = context.model.get_cell(self.cell_addr)
        
        if cell is None:
            #print(f"DEBUG: get_value: No cell found for {self.cell_addr}")
            return None

        # If cell is dirty, force a re-evaluation
        if cell.need_update:
            #print(f"DEBUG: XlReference.get_value: cell {cell_ref} is dirty; calling eval_cell_value.")
            result = context.eval_cell_value(cell)
        else:
            # Otherwise, if the cell has a current value and is not in the evaluation stack,
            # return that value.
            if cell.value is not None and cell_ref not in context._evaluation_stack:
                #print(f"DEBUG: XlReference.get_value: using current cell.value for {cell_ref}: {cell.value}")
                result = cell.value
            else:
                #print(f"DEBUG: XlReference.get_value: recalc fallback for {cell_ref}.")
                result = context.eval_cell_value(cell)

        # Unwrap any nested XlReference
        max_iterations = 100
        iteration = 0
        while isinstance(result, XlReference) and iteration < max_iterations:
            old_result = result
            result = result.get_value(context)
            #print(f"DEBUG: XlReference.get_value: iteration {iteration}: unwrapped {old_result} to {result}")
            iteration += 1

##        if iteration == max_iterations:
##            print("DEBUG: XlReference.get_value: reached maximum iteration limit.")

        #print(f"DEBUG: XlReference.get_value: final result for {cell_ref} is {result}")
        return result


    def __repr__(self):
        return f"<XlReference {self.cell_addr.plain_reference()}>"

# --- New helper class for wrapping arrays (ranges)
class XlArray(XLType):
    # Give our type a high priority so that its operators are used in mixed operations.
    __array_priority__ = 1000

    def __init__(self, data):
        if not hasattr(data, "shape"):
            self.data = np.array(data)
        else:
            self.data = data

    @property
    def shape(self):
        return self.data.shape

    @property
    def flat(self):
        # Provide a flat iterator over the underlying numpy array.
        return self.data.flat

    def __repr__(self):
        return f"<XlArray {self.data!r}>"

    # This method intercepts any numpy ufunc calls on XlArray so that we always work on self.data.
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        # Replace any XlArray inputs with their underlying data.
        new_inputs = [x.data if isinstance(x, XlArray) else x for x in inputs]
        result = getattr(ufunc, method)(*new_inputs, **kwargs)
        # If the result is an ndarray, wrap it in an XlArray.
        if isinstance(result, np.ndarray):
            return XlArray(result)
        else:
            return result

    # Overload the comparison operators so that they return boolean arrays.
    def __gt__(self, other):
        other_data = other.data if isinstance(other, XlArray) else other
        result = np.greater(self.data, other_data)
        return XlArray(result.astype(bool))

    def __lt__(self, other):
        other_data = other.data if isinstance(other, XlArray) else other
        result = np.less(self.data, other_data)
        return XlArray(result.astype(bool))

    def __ge__(self, other):
        other_data = other.data if isinstance(other, XlArray) else other
        result = np.greater_equal(self.data, other_data)
        return XlArray(result.astype(bool))

    def __le__(self, other):
        other_data = other.data if isinstance(other, XlArray) else other
        result = np.less_equal(self.data, other_data)
        return XlArray(result.astype(bool))

    # Reverse operators (for when a scalar is on the left)
    def __rgt__(self, other):
        # This implements: scalar > self
        result = np.greater(other, self.data)
        return XlArray(result.astype(bool))

    def __rlt__(self, other):
        # This implements: scalar < self
        result = np.less(other, self.data)
        return XlArray(result.astype(bool))
