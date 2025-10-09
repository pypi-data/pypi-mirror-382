# information_funcs.py
"""
Excel-like "information" functions, adapted from xlcalculator:
    ISBLANK, ISERR, ISERROR, ISEVEN, ISNUMBER, ISTEXT,
    NA, ISNA, ISODD
Refactored to fit your typed environment (func_xltypes, etc.) 
and removed advanced star-arg usage. 
"""

from . import xl, xlerrors, func_xltypes

@xl.register()
@xl.validate_args
def ISBLANK(cell: func_xltypes.XlAnything) -> func_xltypes.XlBoolean:
    """
    Returns True only if 'cell' is an actual Blank type (or None).
    In real Excel, a cell containing "" is text, so ISBLANK("") => False.
    """
    # By default, func_xltypes.Blank.is_blank(...) returns True 
    # if cell is typed Blank or None. That matches Excel’s definition.
    return func_xltypes.Blank.is_blank(cell)

@xl.register()
@xl.validate_args
def ISBOOLEAN(cell: func_xltypes.XlAnything) -> func_xltypes.XlBoolean:
    """
    Returns True if 'cell' is typed Boolean(...).
    (In standard Excel, the equivalent is ISLOGICAL.)
    """
    return isinstance(cell, func_xltypes.Boolean)
    
@xl.register()
def ISERR(value: func_xltypes.XlAnything) -> func_xltypes.XlBoolean:
    """
    Returns True if 'value' is any ExcelError EXCEPT #N/A.
    https://support.microsoft.com/en-us/office/iserr-function-d8e7d51b-1b33-453d-9b5e-3e9a13c3206c
    """
    if isinstance(value, xlerrors.ExcelError) and not isinstance(value, xlerrors.NaExcelError):
        return True
    return False


@xl.register()
def ISERROR(value: func_xltypes.XlAnything) -> func_xltypes.XlBoolean:
    """
    Returns True if 'value' is ANY ExcelError (including #N/A).
    https://support.microsoft.com/en-us/office/iserror-function-38f1586c-5557-4d39-b5c0-b7f65f41b074
    """
    return isinstance(value, xlerrors.ExcelError)


@xl.register()
@xl.validate_args
def ISEVEN(num: func_xltypes.XlNumber) -> func_xltypes.XlBoolean:
    """
    Returns True if 'num' is an even integer, False otherwise.
    https://support.microsoft.com/en-us/office/iseven-function-aa15929a-d77b-4fbb-92f4-2f479af55356
    """
    # Convert to int, then check if int % 2 == 0
    return (int(num) % 2) == 0


@xl.register()
@xl.validate_args
def ISNUMBER(cell: func_xltypes.XlAnything) -> func_xltypes.XlBoolean:
    """
    Returns True if 'cell' is typed Number(...).
    https://support.microsoft.com/en-us/office/isnumber-function-13eccc54-ed1d-489d-abc8-70a3c514f08f
    """
    return isinstance(cell, func_xltypes.Number)


@xl.register()
@xl.validate_args
def ISTEXT(cell: func_xltypes.XlAnything) -> func_xltypes.XlBoolean:
    """
    Returns True if 'cell' is typed Text(...).
    https://support.microsoft.com/en-us/office/istext-function-a686ce70-6672-4a1f-89ce-e404028da9d2
    """
    return isinstance(cell, func_xltypes.Text)


@xl.register()
@xl.validate_args
def NA() -> xlerrors.ExcelError:
    """
    Returns the #N/A error.
    https://support.microsoft.com/en-us/office/na-function-41242e0e-0686-4c71-a68e-4b3b82f31ff6
    """
    return xlerrors.NaExcelError()


@xl.register()
def ISNA(cell) -> func_xltypes.XlBoolean:
    """
    Returns True if 'cell' is #N/A.
    https://support.microsoft.com/en-us/office/isna-function-80e650f7-7a8f-490f-968a-2fdf72b86679

    We omit @xl.validate_args so that we can pass ExcelError objects directly.
    """
    return isinstance(cell, xlerrors.NaExcelError)


@xl.register()
@xl.validate_args
def ISODD(num: func_xltypes.XlNumber) -> func_xltypes.XlBoolean:
    """
    Returns True if 'num' is odd integer, False if it's even.
    https://support.microsoft.com/en-us/office/isodd-function-1208a56d-4f10-4f44-a5fc-648cafd6c07a
    """
    return (int(num) % 2) != 0

