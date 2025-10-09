# text.py
from typing import Union, Tuple

from . import xl, xlerrors, func_xltypes

@xl.register()
def CONCAT(*args) -> func_xltypes.XlText:
    # We skip @validate_args because it can't handle varargs properly.
    # We'll do manual casting.
    if len(args) > 254:
        raise xlerrors.ValueExcelError(f"Can't concat more than 254 arguments.")

    flattened = xl.flatten(args)
    textified = [func_xltypes.Text.cast(item) for item in flattened]
    return ''.join(str(t) for t in textified)

@xl.register()
def CONCATENATE(*args) -> func_xltypes.XlText:
    # same logic
    flattened = xl.flatten(args)
    textified = [func_xltypes.Text.cast(item) for item in flattened]
    return ''.join(str(t) for t in textified)

@xl.register()
@xl.validate_args
def EXACT(
    text1: func_xltypes.XlText,
    text2: func_xltypes.XlText
) -> func_xltypes.XlBoolean:
    return str(text1) == str(text2)

@xl.register()
@xl.validate_args
def FIND(
    find_text: func_xltypes.XlText,
    within_text: func_xltypes.XlText,
    start_num: func_xltypes.Number = 0
) -> func_xltypes.Number:
    find_str = str(find_text)
    within_str = str(within_text)
    start_int = int(start_num)
    # shift from 1-based to 0-based
    if start_int > 0:
        start_int -= 1

    try:
        pos = within_str.index(find_str, start_int) + 1  # shift back to 1-based
    except ValueError:
        raise xlerrors.ValueExcelError(
            f"Text '{find_str}' not found in '{within_str}' (start={start_int+1})"
        )
    return pos

@xl.register()
@xl.validate_args
def LEFT(
    text: func_xltypes.XlText,
    num_chars: func_xltypes.XlNumber = 1
) -> func_xltypes.XlText:
    return str(text)[:int(num_chars)]

@xl.register()
@xl.validate_args
def LEN(
    text: func_xltypes.XlText
) -> func_xltypes.XlNumber:
    return len(str(text))

@xl.register()
@xl.validate_args
def LOWER(
    text: func_xltypes.XlText
) -> func_xltypes.XlText:
    return str(text).lower()

@xl.register()
@xl.validate_args
def MID(
    text: func_xltypes.XlText,
    start_num: func_xltypes.Number,
    num_chars: func_xltypes.Number
) -> func_xltypes.XlText:
    text_str = str(text)
    from .xl import CELL_CHARACTER_LIMIT
    if len(text_str) > CELL_CHARACTER_LIMIT:
        raise xlerrors.ValueExcelError("Text too long.")
    
    s = int(start_num)
    n = int(num_chars)
    if s<1:
        raise xlerrors.NumExcelError(f"{s} < 1 not allowed.")
    if n<0:
        raise xlerrors.NumExcelError(f"{n} < 0 not allowed.")
    
    start_idx = s-1
    return text_str[start_idx:start_idx+n]

@xl.register()
@xl.validate_args
def REPLACE(
    old_text: func_xltypes.XlText,
    start_num: func_xltypes.XlNumber,
    num_chars: func_xltypes.XlNumber,
    new_text: func_xltypes.XlText
) -> func_xltypes.XlText:
    old_str = str(old_text)
    s = int(start_num) -1
    n = int(num_chars)
    new_str = str(new_text)

    if s<0:
        raise xlerrors.NumExcelError(f"{start_num} < 1 not allowed.")

    if s >= len(old_str):
        # means we are beyond the end => treat as old_str + new_str
        return old_str + new_str

    end_i = s + n
    return old_str[:s] + new_str + old_str[end_i:]

@xl.register()
@xl.validate_args
def RIGHT(
    text: func_xltypes.XlText,
    num_chars: func_xltypes.XlNumber = 1
) -> func_xltypes.XlText:
    t = str(text)
    n = int(num_chars)
    return t[-n:]

@xl.register()
@xl.validate_args
def TRIM(
    text: func_xltypes.XlText
) -> func_xltypes.XlText:
    # Excel's TRIM removes all extra spaces between words.
    parts = str(text).split()
    return " ".join(parts)

@xl.register()
@xl.validate_args
def UPPER(
    text: func_xltypes.XlText
) -> func_xltypes.XlText:
    return str(text).upper()
