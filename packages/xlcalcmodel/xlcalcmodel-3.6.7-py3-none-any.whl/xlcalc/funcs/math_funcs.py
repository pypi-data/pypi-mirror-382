# math_funcs.py
"""
Refactored Excel-like math functions, removing pandas/scipy dependencies and
using only Python's standard library (math, decimal, random).
"""

import decimal
import math
import random  # for RANDBETWEEN, RAND
import numpy as np
import logging
from typing import Tuple, Union, Any
from .func_xltypes import Array

from . import xl, xlerrors, xlcriteria, func_xltypes, information_funcs
from xlcalc.xltypes import XlReference, XlArray

logger = logging.getLogger(__name__)

################################
# Helper: Double Factorial
################################
def double_factorial(n: int) -> int:
    """
    Returns the double factorial of n, i.e. n*(n-2)*(n-4)*... > 0
    Raises if n<0.
    """
    if n < 0:
        raise xlerrors.NumExcelError("Negative values are not allowed for double factorial.")
    if n <= 1:
        return 1
    result = 1
    while n > 1:
        result *= n
        n -= 2
    return result

################################
# Helper: Rounding
################################
def _round(number, num_digits, _rounding=decimal.ROUND_HALF_UP):
    dec_val = decimal.Decimal(str(number))
    with decimal.localcontext() as dc:
        dc.rounding = _rounding
        ans = round(dec_val, int(num_digits))
    return float(ans)

def _round_half_away_from_zero(value: float) -> float:
    """
    Excel's MROUND rounds half away from zero (e.g. 2.5 -> 3, -2.5 -> -3).
    Python's built-in round() is banker's rounding by default, so we implement
    our own to match Excel's behavior exactly.
    """
    if value > 0:
        return math.floor(value + 0.5)
    else:
        return math.ceil(value - 0.5)

@xl.register()
def MROUND(
    number: func_xltypes.XlAnything,
    multiple: func_xltypes.XlAnything,
    context=None  # context parameter for dereferencing
) -> func_xltypes.XlNumber:
    """
    MROUND(number, multiple)

    Rounds 'number' to the nearest multiple of 'multiple'.
      - If 'multiple' == 0, returns 0.
      - If 'number' and 'multiple' have opposite signs, returns #NUM! error.
      - Rounds half away from zero (matching Excel’s behavior).
    """
    from xlcalc.xltypes import XlReference
    from xlcalc.funcs.xlerrors import ValueExcelError, NumExcelError
    import numpy as np

    # --- Propagate errors immediately if any argument is an error ---
    if isinstance(number, ValueExcelError):
        return number
    if isinstance(multiple, ValueExcelError):
        return multiple

     # --- If a numpy string or a normal string, clean it ---
    if isinstance(number, (np.str_, str)):
        number = str(number).strip()
    if isinstance(multiple, (np.str_, str)):
        multiple = str(multiple).strip()

    # --- Dereference if the arguments are XlReference objects ---
    if isinstance(number, XlReference):
        number = context.eval_cell_value(context.model.get_cell(number.get_address()))
    if isinstance(multiple, XlReference):
        multiple = context.eval_cell_value(context.model.get_cell(multiple.get_address()))
    
    # --- Attempt conversion to floats ---
    try:
        num_val = float(number)
        mul_val = float(multiple)
    except Exception as e:
        return ValueExcelError(f"MROUND: Unable to convert arguments to float: {e}")

    # --- Special cases ---
    if num_val == 0:
        return 0.0
    if mul_val == 0:
        return 0.0
    if (num_val < 0 < mul_val) or (mul_val < 0 < num_val):
        return NumExcelError("Number and multiple have different signs.")

    ratio = num_val / mul_val
    ratio_rounded = _round_half_away_from_zero(ratio)
    return ratio_rounded * mul_val

@xl.register()
def N(*args):
    """
    Excel-like N function:
      - If no arguments, return 0.
      - If more than one argument, treat them as an array.
      - If the single argument is an array (a list or an XlArray), map N element‐by‐element.
      - Otherwise, convert a scalar.
    """
    from xlcalc.xltypes import XlReference, XlArray

    if not args:
        return 0

    if len(args) > 1:
        # treat multiple arguments as an array
        return [N(x) for x in args]

    # Only one argument:
    val = args[0]

    # If the argument is an XlArray, convert it elementwise.
    if isinstance(val, XlArray):
        # We use numpy.vectorize to apply _scalar_N to every element.
        import numpy as np
        def convert_element(x):
            return _scalar_N(x)
        new_data = np.vectorize(convert_element)(val.data)
        return XlArray(new_data)
    
    # If it is a plain list, assume it is a 2D array and process it recursively.
    if isinstance(val, list):
        return _arrayify_N(val)

    # Otherwise handle a single scalar value.
    return _scalar_N(val)

def _arrayify_N(arr):
    """
    Recursively apply _scalar_N to each element if it's a sublist
    """
    if not isinstance(arr, list):
        return _scalar_N(arr)
    return [ _arrayify_N(x) for x in arr ]

def _scalar_N(val):
    """
    Convert a single scalar to a number per Excel's N() rules:
      - error => return the error as-is
      - number => same number
      - boolean => 1 or 0
      - text => 0
      - blank => 0
      - anything else => 0
    """
    if xlerrors.ExcelError.is_error(val):
        # In Excel, #N/A remains #N/A, #REF! remains #REF!, etc.
        return val
    elif information_funcs.ISBOOLEAN(val) or isinstance(val, bool):
        return 1.0 if bool(val) else 0.0
    elif information_funcs.ISNUMBER(val) or isinstance(val, (int, float)):
        return float(val)
    elif information_funcs.ISTEXT(val) or isinstance(val, str):
##    elif information_funcs.ISNUMBER(val):
##        return val
##    elif information_funcs.ISBOOLEAN(val):
##        return 1.0 if val else 0.0
##    elif information_funcs.ISTEXT(val):
        return 0.0
    elif information_funcs.ISBLANK(val):
        return 0.0
    # fallback
    return 0.0


################################
# MATH FUNCTIONS
################################

@xl.register()
@xl.validate_args
def ABS(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return abs(float(number))

@xl.register()
@xl.validate_args
def ACOS(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    # arcsine's domain is [-1,1], so check
    # We'll let math.acos() raise ValueError if out of domain
    return math.acos(float(number))

@xl.register()
@xl.validate_args
def ACOSH(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    # acosh domain: x >= 1
    if number < 1:
        raise xlerrors.NumExcelError(f"ACOSH domain error: number {number} < 1")
    return math.acosh(float(number))

@xl.register()
@xl.validate_args
def ASIN(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    # domain: -1 <= x <= 1
    if float(number) < -1.0 or float(number) > 1.0:
        raise xlerrors.NumExcelError(f"ASIN domain error: {number} out of [-1,1]")
    return math.asin(float(number))

@xl.register()
@xl.validate_args
def ASINH(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.asinh(float(number))

@xl.register()
@xl.validate_args
def ATAN(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.atan(float(number))

@xl.register()
@xl.validate_args
def ATAN2(x_num: func_xltypes.XlNumber, y_num: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.atan2(float(x_num), float(y_num))

@xl.register()
@xl.validate_args
def CEILING(number: func_xltypes.XlNumber, significance: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    if significance == 0:
        return 0
    f_number = float(number)
    f_sign = float(significance)

    if f_sign < 0 < f_number:
        raise xlerrors.NumExcelError("significance below zero and number above zero not allowed")

    # do actual math
    # e.g. Excel: CEILING(2.3,1)=3
    # We'll do round away from zero
    result = f_sign * math.ceil(f_number / f_sign)
    # Optional: handle negative sign intricacies with decimal if needed
    return result

@xl.register()
@xl.validate_args
def COS(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.cos(float(number))

@xl.register()
@xl.validate_args
def COSH(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.cosh(float(number))

@xl.register()
@xl.validate_args
def DEGREES(angle: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.degrees(float(angle))

@xl.register()
@xl.validate_args
def EVEN(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    fval = float(number)
    if fval < 0:
        return math.ceil(abs(fval)/2)*-2
    else:
        return math.ceil(fval/2)*2

@xl.register()
@xl.validate_args
def EXP(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.exp(float(number))

@xl.register()
@xl.validate_args
def FACT(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    if number < 0:
        raise xlerrors.NumExcelError("Negative values not allowed for FACT.")
    return math.factorial(int(number))

@xl.register()
@xl.validate_args
def FACTDOUBLE(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    if number < 0:
        raise xlerrors.NumExcelError("Negative values not allowed for FACTDOUBLE.")
    return float(double_factorial(int(number)))

@xl.register()
@xl.validate_args
def FLOOR(number: func_xltypes.XlNumber, significance: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    f_num = float(number)
    f_sig = float(significance)
    if f_sig < 0 < f_num:
        raise xlerrors.NumExcelError("number & significance must have same sign or zero.")
    if f_num == 0:
        return 0.0
    if f_sig == 0:
        raise xlerrors.DivZeroExcelError()

    return f_sig * math.floor(f_num/f_sig)

@xl.register()
@xl.validate_args
def INT(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    # Round down to nearest integer
    fval = float(number)
    if fval < 0:
        return _round(fval, 0, _rounding=decimal.ROUND_UP)
    else:
        return _round(fval, 0, _rounding=decimal.ROUND_DOWN)

@xl.register()
@xl.validate_args
def LN(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.log(float(number))

@xl.register()
@xl.validate_args
def LOG(number: func_xltypes.XlNumber, base: func_xltypes.XlNumber = 10) -> func_xltypes.XlNumber:
    return math.log(float(number), float(base))

@xl.register()
@xl.validate_args
def LOG10(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.log10(float(number))

@xl.register()
@xl.validate_args
def MOD(number: func_xltypes.XlNumber, divisor: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return float(number) % float(divisor)

@xl.register()
@xl.validate_args
def RAND() -> func_xltypes.XlNumber:
    """ Return a random float >=0 and <1 """
    return random.random()

@xl.register()
@xl.validate_args
def RANDBETWEEN(bottom: func_xltypes.XlNumber, top: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    """ Return a random integer in [bottom..top]. """
    b = float(bottom)
    t = float(top)
    return int(random.random()*(t - b) + b)

@xl.register()
def PI() -> func_xltypes.XlNumber:
    return math.pi

@xl.register()
@xl.validate_args
def POWER(number: func_xltypes.XlNumber, power: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return float(number) ** float(power)

@xl.register()
@xl.validate_args
def RADIANS(angle: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.radians(float(angle))

@xl.register()
#@xl.validate_args
def ROUND(number: func_xltypes.XlNumber, num_digits: func_xltypes.XlNumber = 0,
          _rounding=decimal.ROUND_HALF_UP) -> func_xltypes.XlNumber:
    return _round(number, num_digits, _rounding=_rounding)

@xl.register()
#@xl.validate_args
def ROUNDUP(number: func_xltypes.XlNumber, num_digits: func_xltypes.XlNumber = 0) -> func_xltypes.XlNumber:
    return _round(number, num_digits, _rounding=decimal.ROUND_UP)

@xl.register()
#@xl.validate_args
def ROUNDDOWN(number: func_xltypes.XlNumber, num_digits: func_xltypes.XlNumber = 0) -> func_xltypes.XlNumber:
    return _round(number, num_digits, _rounding=decimal.ROUND_DOWN)

@xl.register()
@xl.validate_args
def SIGN(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    fval = float(number)
    if fval > 0:
        return 1.0
    elif fval < 0:
        return -1.0
    return 0.0

@xl.register()
@xl.validate_args
def SIN(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.sin(float(number))

@xl.register()
@xl.validate_args
def SQRT(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    if number < 0:
        raise xlerrors.NumExcelError(f"number {number} must be non-negative.")
    return math.sqrt(float(number))

@xl.register()
@xl.validate_args
def SQRTPI(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    if number < 0:
        raise xlerrors.NumExcelError(f"number {number} must be non-negative.")
    return math.sqrt(float(number) * math.pi)

@xl.register()
#@xl.validate_args
def SUM(*args: func_xltypes.XlAnything, context=None) -> func_xltypes.XlNumber:
    """
    Returns the sum of all numeric items passed in.
    If an argument is an array (or nested list), it is flattened first.

    The extra 'context' keyword parameter is accepted (but not used) to allow
    the evaluator to pass it without error.
    """
    total = 0.0
    for arg in args:
        # If the argument has a .flat attribute (e.g. an XlArray), iterate over it.
        if hasattr(arg, "flat"):
            #print(f"SUM debug: Processing XlArray with flat = {arg.flat}")
            logger.debug("SUM debug: Processing XlArray with flat = %s", arg.flat)
            for value in arg.flat:
                try:
                    total += float(value)
                except (ValueError, TypeError):
                    total += 0.0
        # If the argument is a plain list (or nested list), flatten it.
        elif isinstance(arg, list):
            from .evaluator import flatten_array  # Import here to avoid circular dependencies
            flat_values = flatten_array(arg)
            #print(f"SUM debug: Processing list, flattened to {flat_values}")
            logger.debug("SUM debug: Processing list, flattened to %s", flat_values)
            for value in flat_values:
                try:
                    total += float(value)
                except (ValueError, TypeError):
                    total += 0.0
        else:
            try:
                total += float(arg)
            except (ValueError, TypeError):
                total += 0.0
    #print(f"SUM debug: final total = {total}")
    logger.debug("SUM debug: final total = %s", total)
    return total

@xl.register()
@xl.validate_args
def SUMIF(
    range: func_xltypes.XlArray,
    criteria: func_xltypes.XlAnything,
    sum_range: func_xltypes.XlArray = None
) -> func_xltypes.XlNumber:
    check = xlcriteria.parse_criteria(criteria)
    if sum_range is None:
        sum_range = range
    rng_flat = range.flat
    sum_flat = sum_range.flat  # We'll cast to float on the fly
    total = 0.0

    for (cval, sval) in zip(rng_flat, sum_flat):
        if check(cval):
            # attempt numeric cast for 'sval'
            try:
                f = float(func_xltypes.Number.cast_from_native(sval))
            except xlerrors.ExcelError:
                f = 0.0
            total += f
    return total

@xl.register()
@xl.validate_args
def SUMIFS(
    sum_range: func_xltypes.XlArray,
    criteria_range: func_xltypes.XlArray,
    criteria: func_xltypes.XlAnything,
    *rest
) -> func_xltypes.XlNumber:
    check1 = xlcriteria.parse_criteria(criteria)
    range1 = criteria_range.flat

    # We'll build up a list of ranges + check functions
    rngs = [range1]
    checks = [check1]

    # parse the rest in pairs => (criteria_range, criteria)
    if len(rest) % 2 != 0:
        raise xlerrors.ValueExcelError("SUMIFS expects even # of extra arguments (range, criteria).")

    # We'll do the same approach as your code:
    # but we won't create partial newRange. We'll parse in pairs.
    i = 0
    extra = list(rest)
    while i < len(extra):
        arr_i = extra[i]
        crit_i = extra[i+1]
        if not isinstance(arr_i, func_xltypes.Array):
            raise xlerrors.ValueExcelError("SUMIFS expects each range to be an XlArray.")
        rngs.append(arr_i.flat)
        checks.append(xlcriteria.parse_criteria(crit_i))
        i += 2

    sum_flat = sum_range.flat
    # We'll iterate zip of each row => ( range1[idx], range2[idx], ... ), sum_range[idx]
    total = 0.0

    for idx, sval in enumerate(sum_flat):
        # check if all criteria pass
        if all(checks[j](rngs[j][idx]) for j in range(len(checks))):
            # add sval if numeric
            try:
                f = float(func_xltypes.Number.cast_from_native(sval))
            except xlerrors.ExcelError:
                f = 0.0
            total += f
    return total

@xl.register()
##def SUMPRODUCT(*arrays: func_xltypes.XlArray, context=None) -> func_xltypes.XlNumber:
def SUMPRODUCT(*arrays: Any, context=None) -> float:
    """
    Returns the sum of products across corresponding cells of one or more arrays.
    All arrays must have the same shape or be broadcastable (scalars will be broadcast).
    
    The function:
      1. Checks if any argument is an XlReference and dereferences it using the provided context.
      2. Converts each argument to an Array (using func_xltypes.Array.cast) if needed.
      3. Broadcasts scalar arrays (shape (1,1)) to the shape of the first array if necessary.
      4. Validates that all arrays have the same shape.
      5. Iterates over each cell in the arrays, dereferencing any cell value that is an XlReference,
         casting it to a number, multiplying corresponding cells, and summing up the results.
    """
    import logging
    logger = logging.getLogger(__name__)
    import numpy as np

    # — unify everything to your Array type —
    new_arrays = []
    for arr in arrays:
        # 1) if it’s a reference, deref it
        if isinstance(arr, XlReference):
            arr = arr.get_value(context)
        # 2) if it’s an XlArray, pull out the raw python nested list
        if isinstance(arr, XlArray):
            arr = arr.data.tolist()
        # 3) cast whatever’s left (list, tuple, scalar) into your Array class
        arr = Array.cast(arr)
        new_arrays.append(arr)
    arrays = new_arrays
    
    # Step 1: Convert each argument into an array. Also, if an argument is an XlReference,
    # use get_value(context) to dereference it.
    converted_arrays = []
    for arr in arrays:
        if isinstance(arr, XlReference):
            logger.debug("SUMPRODUCT: Dereferencing XlReference argument: %s", arr)
            arr = arr.get_value(context)
        if not hasattr(arr, "shape"):
            arr = func_xltypes.Array.cast(arr)
            logger.debug("SUMPRODUCT: Converted argument to Array: %s", arr)
        converted_arrays.append(arr)
    arrays = converted_arrays

    if len(arrays) == 0:
        raise xlerrors.NullExcelError("SUMPRODUCT requires at least one array argument.")

    # Step 2: Broadcast any scalar arrays (shape (1,1)) to the shape of the first array.
    shape0 = arrays[0].shape
    for i in range(len(arrays)):
        if arrays[i].shape == (1,1) and shape0 != (1,1):
            scalar_val = arrays[i].data[0, 0]
            new_data = np.full(shape0, scalar_val, dtype=object)
            arrays[i] = func_xltypes.Array(new_data)
            logger.debug("SUMPRODUCT: Broadcasting argument %d to shape %s", i, shape0)

    # Step 3: Check that all arrays have the same shape.
    shape0 = arrays[0].shape  # re-read in case it was updated
    for arr in arrays:
        if arr.shape != shape0:
            raise xlerrors.ValueExcelError(f"SUMPRODUCT array shape mismatch. {shape0} vs {arr.shape}")
        # Also check if any cell is an ExcelError.
        for cell_val in arr.flat:
            if isinstance(cell_val, xlerrors.ExcelError):
                raise xlerrors.NaExcelError("Excel Error found in SUMPRODUCT array cell.")

    # Step 4: Multiply corresponding cells and sum the products.
    nrows, ncols = shape0
    total = 0.0
    for r in range(nrows):
        for c in range(ncols):
            product = 1.0
            for arr in arrays:
                try:
                    # Get the value at row r, column c.
                    val = arr.data[r, c]
                except Exception as e:
                    logger.error("SUMPRODUCT: Error accessing cell at row %s, col %s: %s", r, c, e)
                    val = 0.0
                # If the value is still an XlReference, dereference it.
                if hasattr(val, "get_value"):
                    logger.debug("SUMPRODUCT: Dereferencing cell value at row %s, col %s: %s", r, c, val)
                    val = val.get_value(context)
                try:
                    # Instead of using cast_from_native, try a direct conversion:
                    fval = float(val)
                except Exception as e:
                    logger.error("SUMPRODUCT: Could not convert value %r at row %s, col %s to float: %s", val, r, c, e)
                    fval = 0.0
                product *= fval
            logger.debug("SUMPRODUCT: Row %s, col %s product = %s", r, c, product)
            total += product
    logger.debug("SUMPRODUCT: Final total = %s", total)
    return total

@xl.register()
@xl.validate_args
def TAN(number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    return math.tan(float(number))

@xl.register()
@xl.validate_args
def TRUNC(
    number: func_xltypes.XlNumber,
    num_digits: func_xltypes.XlNumber = 0
) -> func_xltypes.XlNumber:
    """
    Trunc a number to specified decimal places.
    If num_digits=0 => int trunc.
    """
    fval = float(number)
    nd = int(float(num_digits))
    if nd == 0:
        return float(math.trunc(fval))
    # e.g. TRUNC(123.456,2)=123.45
    power = 10**nd
    tmp = math.trunc(fval*power)/power
    return tmp
