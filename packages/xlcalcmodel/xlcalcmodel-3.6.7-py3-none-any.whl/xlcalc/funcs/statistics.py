# statistics.py
"""
Excel-like statistical and counting functions adapted from xlcalculator,
using your typed approach (xl.py, xlerrors.py, func_xltypes.py)
and the new flatten logic to handle arrays.
"""

from typing import Union
from . import xl, xlerrors, func_xltypes, xlcriteria
import logging

logger = logging.getLogger(__name__)

def _try_cast_number(val) -> float:
    """
    Attempt to cast 'val' to a typed Number. If successful, return float(value).
    Otherwise, raise or skip as needed.
    """
    try:
        # If cast_from_native fails, it raises ValueExcelError for non-numbers
        typed_val = func_xltypes.Number.cast_from_native(val)
        return float(typed_val)
    except xlerrors.ExcelError:
        # means 'val' isn't numeric
        raise

@xl.register()
def AVERAGE(*args) -> func_xltypes.XlNumber:
    """
    Returns the average (arithmetic mean) of the arguments or 0 if none.
    Accepts multiple numeric arguments or arrays, e.g. AVERAGE(1,2,3,4)
    or AVERAGE([[10,20],[30,40]]).
    """
    flattened = xl.flatten(args)
    numeric_values = []
    for v in flattened:
        try:
            numeric_values.append(_try_cast_number(v))
        except xlerrors.ExcelError:
            # skip non-numeric
            pass
    if not numeric_values:
        return 0.0
    return sum(numeric_values)/len(numeric_values)

@xl.register()
def COUNT(*args) -> func_xltypes.XlNumber:
    """
    Counts how many items are numeric.
    https://support.office.com/en-us/article/count-function-a59cd7fc-b623-4d93-87a4-d23bf411294c
    """
    flattened = xl.flatten(args)
    if not flattened:
        raise xlerrors.ValueExcelError("At least one argument is required for COUNT.")
    if len(flattened) > 255:
        raise xlerrors.ValueExcelError(
            f"COUNT can only handle up to 255 arguments, got {len(flattened)}"
        )

    numeric_count = 0
    for v in flattened:
        try:
            _ = _try_cast_number(v)
            numeric_count += 1
        except xlerrors.ExcelError:
            pass
    return float(numeric_count)

@xl.register()
def COUNTA(*args) -> func_xltypes.XlNumber:
    """
    Counts how many arguments are not blank.
    https://support.office.com/en-us/article/counta-function-7dc98875-d5c1-46f1-9a82-53f3219e2509
    """
    flattened = xl.flatten(args)
    if not flattened:
        raise xlerrors.NullExcelError("At least one argument is required for COUNTA.")
    if len(flattened) > 256:
        raise xlerrors.ValueExcelError(
            f"COUNTA can handle up to 256 arguments, got {len(flattened)}"
        )

    non_blank = [v for v in flattened if not func_xltypes.Blank.is_blank(v)]
    return float(len(non_blank))

@xl.register()
@xl.validate_args
def COUNTIF(
    count_range: func_xltypes.XlArray,
    criteria: func_xltypes.XlAnything
) -> func_xltypes.XlNumber:
    """
    Counts how many items in count_range meet the condition in 'criteria'.
    https://support.microsoft.com/en-us/office/countif-function-e0de10c6-f885-4e71-abb4-1f464816df34
    """
    check_fn = xlcriteria.parse_criteria(criteria)
    arr = count_range.flat
    # Just apply the condition to each cell
    return sum(check_fn(x) for x in arr)


@xl.register()
@xl.validate_args
def COUNTIFS(
    count_range1: func_xltypes.XlArray,
    criteria1: func_xltypes.XlAnything,
    *rest
) -> func_xltypes.XlNumber:
    """
    Counts how many items meet multiple conditions.
    e.g. COUNTIFS(A, ">10", B, "Yes", [C, "<=5"], ...)
    https://support.microsoft.com/en-us/office/countifs-function-dda3dc6e-f74e-4aee-88bc-aa8c2a866842
    """
    # Parse first range+criteria
    check1 = xlcriteria.parse_criteria(criteria1)
    ranges = [count_range1.flat]
    checks = [check1]

    # 'rest' should come in pairs => (range, criteria)
    if len(rest) % 2 != 0:
        raise xlerrors.ValueExcelError(
            "COUNTIFS expects an even number of extra arguments (range, criteria)."
        )

    # Build up ranges[] + checks[] from the pairs
    for i in range(0, len(rest), 2):
        arr_i = rest[i]
        crit_i = rest[i+1]
        if not isinstance(arr_i, func_xltypes.Array):
            raise xlerrors.ValueExcelError(
                "COUNTIFS expects each 'range' argument to be an XlArray."
            )
        ranges.append(arr_i.flat)
        checks.append(xlcriteria.parse_criteria(crit_i))

    # Ensure all ranges have the same length => typical Excel requirement
    row_count = len(ranges[0])
    for rng in ranges:
        if len(rng) != row_count:
            raise xlerrors.ValueExcelError(
                "All ranges in COUNTIFS must have the same length/dimensions."
            )

    # Now zip across each row
    count = 0
    for idx in range(row_count):
        # Gather each range's value at row=idx
        row_vals = [rng[idx] for rng in ranges]
        # If all checks pass => increment
        if all(checks[j](row_vals[j]) for j in range(len(checks))):
            count += 1

    return float(count)

@xl.register()
def MAX(*args, context=None) -> func_xltypes.XlNumber:
    """
    Return the maximum of numeric arguments, or 0 if none.
    """
    # Use our improved flatten_array to process the arguments.
    from xlcalc.evaluator import flatten_array  # adjust import as needed
    #print(f"DEBUG: MAX called with args: {args}")
    logger.debug(f"MAX called with args: {args}")
    flattened = flatten_array(args)
    #print(f"DEBUG: Flattened args: {flattened}")
    logger.debug(f"Flattened args: {flattened}")

    numeric_values = []
    for v in flattened:
        try:
            # _try_cast_number should convert v to a float if possible.
            cast_value = _try_cast_number(v)
            numeric_values.append(cast_value)
            #print(f"DEBUG: Successfully cast {v} to {cast_value}")
            logger.debug(f"Successfully cast {v} to {cast_value}")
        except xlerrors.ExcelError as e:
            #print(f"DEBUG: Failed to cast {v} to a number: {e}")
            logger.debug(f"Failed to cast {v} to a number: {e}")
            
    #print(f"DEBUG: Numeric values collected: {numeric_values}")
    logger.debug(f"Numeric values collected: {numeric_values}")

    if not numeric_values:
        #print("DEBUG: No numeric values found, returning 0.0")
        logger.debug("No numeric values found, returning 0.0")
        return 0.0

    result = max(numeric_values)
    #print(f"DEBUG: MAX computed result: {result}")
    logger.debug(f"MAX computed result: {result}")
    return result


@xl.register()
def MIN(*args, context=None) -> func_xltypes.XlNumber:
    """
    Return the minimum of numeric arguments, or 0 if none.
    
    If any argument is an Excel error (e.g. a ValueExcelError),
    that error is immediately propagated.
    
    Non-numeric values (such as text) are ignored, as in Excel.
    https://support.office.com/en-us/article/min-function-61635d12-920f-4ce2-a70f-96f202dcc152
    """
    # Use the improved flatten_array function to unwrap all arguments.
    from xlcalc.evaluator import flatten_array
    #print(f"DEBUG: MIN called with args: {args}")
    logger.debug(f"MIN called with args: {args}")
    flattened = flatten_array(args)
    #print(f"DEBUG: Flattened args: {flattened}")
    logger.debug(f"Flattened args: {flattened}")

    numeric_values = []
    for v in flattened:
        # If the value is already an Excel error, propagate it immediately.
        if isinstance(v, xlerrors.ExcelError):
            return v
        try:
            num = _try_cast_number(v)
            numeric_values.append(num)
            #print(f"DEBUG: Successfully cast {v} to {num}")
            logger.debug(f"Successfully cast {v} to {num}")
        except xlerrors.ExcelError:
            # If conversion fails, then v is non-numeric (like text) so ignore it.
            continue
    #print(f"DEBUG: Numeric values collected: {numeric_values}")
    logger.debug(f"Numeric values collected: {numeric_values}")
    
    if not numeric_values:
        #print("DEBUG: No numeric values found, returning 0.0")
        logger.debug("No numeric values found, returning 0.0")
        return 0.0

    result = min(numeric_values)
    #print(f"DEBUG: MIN computed result: {result}")
    logger.debug(f"MIN computed result: {result}")
    return result
