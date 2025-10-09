# xlcriteria.py
#Latest
import re

from . import xlerrors, func_xltypes

CRITERIA_REGEX = r'(\W*)(.*)'

def _op_lt(a, b): return a < b
def _op_le(a, b): return a <= b
def _op_eq(a, b): return a == b
def _op_ne(a, b): return a != b
def _op_ge(a, b): return a >= b
def _op_gt(a, b): return a > b

CRITERIA_OPERATORS = {
    '<':  _op_lt,
    '<=': _op_le,
    '=':  _op_eq,
    '<>': _op_ne,
    '>=': _op_ge,
    '>':  _op_gt,
}

def parse_criteria(criteria):
    """
    Returns a check(...) -> bool function that tests if 'x' meets the condition in 'criteria'.
    e.g. criteria=">=5", parse-> operator= _op_ge, value=Number(5),
    check(x)-> typed_probe >= Number(5)
    """
    # if it's a string => parse something like ">=5" or "5" => interpret as '='5
    if isinstance(criteria, (str, func_xltypes.Text)):
        match = re.search(CRITERIA_REGEX, str(criteria))
        if not match:
            # interpret entire string as '='
            str_op = '='
            str_val = str(criteria)
        else:
            str_op, str_val = match.group(1), match.group(2)

        op_fn = CRITERIA_OPERATORS.get(str_op)
        if not op_fn:
            # fallback => '=' entire string
            op_fn = _op_eq
            str_val = criteria

        # Attempt cast str_val to Number/DateTime/Boolean
        val = str_val
        for XlType in (func_xltypes.Number, func_xltypes.DateTime, func_xltypes.Text, 
                       func_xltypes.Boolean):
            try:
                val = XlType.cast(str_val)
                break
            except xlerrors.ValueExcelError:
                pass

        def check_fn(probe):
            typed_probe = func_xltypes.ExcelType.cast_from_native(probe)
    
            # If operator is numeric AND either side is not Number (or DateTime, if you want date comparisons),
            # then we skip it (return False).
            if op_fn in (_op_lt, _op_le, _op_gt, _op_ge):
                # If either 'typed_probe' or 'val' is not numeric, do NOT count it
                if not (isinstance(typed_probe, func_xltypes.Number) 
                        and isinstance(val, func_xltypes.Number)):
                    return False
    
            return bool(op_fn(typed_probe, val))

        return check_fn

    # If not a string => cast to ExcelType
    casted = func_xltypes.ExcelType.cast_from_native(criteria)
    
    # If it's an Array => not supported
    if isinstance(casted, func_xltypes.Array):
        raise xlerrors.ValueExcelError("Array criteria not supported in parse_criteria.")

    # fallback => equality check with that casted object
    def check_fn2(x):
        typed_probe = func_xltypes.ExcelType.cast_from_native(x)
        return typed_probe == casted

    return check_fn2
