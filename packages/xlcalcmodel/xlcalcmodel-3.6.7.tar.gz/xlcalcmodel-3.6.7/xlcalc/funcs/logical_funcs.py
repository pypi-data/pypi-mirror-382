# logical_funcs.py

"""
Usage:
 - AND(*args) -> bool
 - OR(*args) -> bool
 - IF(logical_test, value_if_true, value_if_false) -> any
 - NOT(value) -> bool
 - TRUE() -> True
 - FALSE() -> False
"""

from . import xl, xlerrors, func_xltypes
from xlcalc.evaluator import flatten_array
import logging

@xl.register()
def AND(*args) -> bool:
    """
    Excel-like AND:
      - If no arguments => #NULL! error
      - skip blank
      - if item is a Python bool => cast to func_xltypes.Boolean
      - if not typed Boolean => #VALUE! error
      - if any boolean is False => entire AND => False
      - else True
    """
    if not args:
        raise xlerrors.NullExcelError("AND requires at least one argument")

    for arg in args:
        val = _eval_expr(arg)
        for item in xl.flatten([val]):
            # 1) skip blank cells
            if func_xltypes.Blank.is_blank(item):
                continue

            # 2) if a built-in bool, convert it
            if isinstance(item, bool):
                item = func_xltypes.Boolean(item)
            # 3) if a number, convert it (Excel treats nonzero as TRUE)
            elif isinstance(item, (int, float)):
                item = func_xltypes.Boolean(bool(item))
            # 4) if still not a typed Boolean, then it’s an error
            elif not isinstance(item, func_xltypes.Boolean):
                raise xlerrors.ValueExcelError("AND encountered non-boolean => #VALUE!")

            # 5) if the Boolean value is False, return False immediately
            if not item.value:
                return False

    return True

@xl.register()
def OR(*args) -> bool:
    """
    Excel-like OR:
      - If no arguments => #NULL! error
      - Skip blank cells.
      - If an item is a Python bool, cast it to a typed Boolean.
      - If a number is encountered, convert it to a Boolean (0 => False, nonzero => True).
      - If an item is not a typed Boolean, then it’s an error.
      - If any Boolean is True, return True immediately; otherwise False.
    """
    if not args:
        raise xlerrors.NullExcelError("OR requires at least one argument")

    for arg in args:
        val = _eval_expr(arg)
        # Use our flatten_array so that XlArray objects are unwrapped properly.
        for item in flatten_array([val]):
            # 1) Skip blank cells.
            if func_xltypes.Blank.is_blank(item):
                continue

            # 2) If a built-in bool, convert it.
            if isinstance(item, bool):
                item = func_xltypes.Boolean(item)
            # 3) If a number, convert it.
            elif isinstance(item, (int, float)):
                item = func_xltypes.Boolean(bool(item))
            # 4) If not a typed Boolean, then it’s an error.
            elif not isinstance(item, func_xltypes.Boolean):
                raise xlerrors.ValueExcelError("OR encountered non-boolean => #VALUE!")

            # 5) If the Boolean value is True, return True immediately.
            if item.value:
                return True

    return False

@xl.register()
def IFERROR(
    value: func_xltypes.XlAnything,
    value_if_error: func_xltypes.XlAnything,
    context=None
) -> func_xltypes.XlAnything:
    """
    IFERROR(value, value_if_error)

    Returns value if it's not an error; otherwise, returns value_if_error.
    Additionally, if value is None or a string error (like "n/a" or "none"),
    then value_if_error is returned.
    
    https://support.microsoft.com/en-us/office/iferror-function-39f8d8d1-76a7-4bf8-a020-89b818d8b402
    """
    # Check if 'value' is an Excel error or a "bad" value
    if (xlerrors.ExcelError.is_error(value) or 
        value is None or 
        (isinstance(value, str) and value.lower() in ("n/a", "none"))):
        return value_if_error
    else:
        return value

@xl.register()
def IF(
    logical_test,
    value_if_true=True,
    value_if_false=False,
    context=None  # so that we can pass context to get_value
):
    logging.debug("IF: Entering IF with logical_test=%s, value_if_true=%s, value_if_false=%s", logical_test, value_if_true, value_if_false)
    
    # Evaluate the condition.
    cond_val = _eval_expr(logical_test)
    logging.debug("IF: Condition evaluated to: %s", cond_val)
    
    # Determine truthiness (using _any_true which flattens arrays and skips blanks)
    is_true = _any_true(cond_val)
    logging.debug("IF: _any_true result: %s", is_true)
    
    # Select the appropriate branch.
    branch = value_if_true if is_true else value_if_false
    logging.debug("IF: Selected branch: %s", branch)
    
    # Evaluate the branch.
    result = _eval_expr(branch)
    logging.debug("IF: After _eval_expr, result is: %s (type %s)", result, type(result))
    
    # If result is still a reference, keep dereferencing until we get a plain value.
    while hasattr(result, "get_value"):
        new_val = result.get_value(context)
        logging.debug("IF: Dereferencing result: current=%s, new=%s (type %s)", result, new_val, type(new_val))
        if new_val == result:
            break
        result = new_val

    logging.debug("IF: Final dereferenced result: %s", result)
    
    # If the result is None or an error string, return 0.
    if result is None or (isinstance(result, str) and result.lower() in ("n/a", "none")):
        logging.debug("IF: Result is None or an error string; returning 0")
        return 0

    logging.debug("IF: Returning final result: %s", result)
    return result

@xl.register()
def NOT(value) -> func_xltypes.XlBoolean:
    """
    Returns the inverse of the boolean representation of value.
    Like Excel's NOT function.
    """
    val = _eval_expr(value)
    # Convert the result to a typed Boolean before returning
    return func_xltypes.Boolean(not bool(_any_true(val)))

@xl.register()
def TRUE() -> func_xltypes.XlBoolean:
    return func_xltypes.Boolean(True)

@xl.register()
def FALSE() -> func_xltypes.XlBoolean:
    return func_xltypes.Boolean(False)

############################
# Internal Helper Functions
############################

def _eval_expr(expr):
    """
    If 'expr' is a callable (like an XlExpr), call it to get the actual value.
    Otherwise return 'expr' directly.
    """
    # This is a minimal approach: in xlcalculator, XlExpr
    # might store 'expr()' as an expression. If you have a different system,
    # adapt accordingly.
    if callable(expr):
        return expr()  # evaluate
    return expr

def _any_true(val):
    """
    Flatten 'val' if needed, ignoring blanks. Return True if any item is true.
    """
    for item in xl.flatten([val]):
        if func_xltypes.Blank.is_blank(item):
            continue
        if bool(item):
            return True
    return False
