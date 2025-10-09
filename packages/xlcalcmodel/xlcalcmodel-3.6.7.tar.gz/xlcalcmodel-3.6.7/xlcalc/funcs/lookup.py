# lookup.py
import re
from . import xl, xlerrors, func_xltypes
from ..references import CellAddress, col_letters_to_num
import numpy as np

def resolve_defined_name(context, name_str: str) -> CellAddress:
    """
    Look up a defined name in the model.
    This function assumes that the workbook model keeps a dictionary of defined names,
    for example as context.model.defined_names mapping name strings to CellAddress objects.
    """
    try:
        cell = context.model.defined_names[name_str]
        if not isinstance(cell, CellAddress):
            raise xlerrors.ValueExcelError(f"Defined name '{name_str}' does not refer to a valid cell address.")
        return cell
    except KeyError:
        raise xlerrors.ValueExcelError(f"Defined name '{name_str}' not found.")

@xl.register()
def ROW(ref: func_xltypes.XlAnything, context=None) -> func_xltypes.XlNumber:
    """
    Returns the row number of the given cell reference.
    
    - If the argument is an XlReference, it extracts its underlying CellAddress and returns its row.
    - If the argument is a CellAddress or a string that can be parsed as one, it returns the row.
    - If the argument is a defined name, it looks up the cell.
    - If the argument is numeric, it attempts to derive the current cell reference from the evaluation context.
    """
    if ref is None:
        raise xlerrors.ValueExcelError("ROW requires a cell reference argument.")

    # If ref is an instance of XlReference, extract its underlying CellAddress.
    from xlcalc.xltypes import XlReference  # Ensure correct import
    if isinstance(ref, XlReference):
        cell = ref.get_address()
        if not cell.sheet:
            cell.sheet = context.sheet
        return float(cell.row)

    # If ref is already a CellAddress, use it.
    if isinstance(ref, CellAddress):
        return float(ref.row)

    # If ref is a string that looks like a cell reference.
    if isinstance(ref, str):
        if re.match(r"^\$?[A-Za-z]{1,3}\$?\d+$", ref):
            try:
                cell = CellAddress.from_string(ref)
                return float(cell.row)
            except Exception as e:
                raise xlerrors.ValueExcelError(f"Invalid cell reference in ROW: {ref}") from e
        else:
            # Assume it's a defined name.
            if context is None:
                raise xlerrors.ValueExcelError("ROW cannot resolve a defined name without an evaluation context.")
            try:
                # Assuming your model has a method to resolve defined names.
                cell = context.model.resolve_defined_name(ref, context.sheet)
                return float(cell.row)
            except Exception as e:
                raise xlerrors.ValueExcelError(f"Invalid cell reference or defined name in ROW: {ref}") from e

    # If ref is numeric, fallback to use the current cell reference from the evaluation context.
    if isinstance(ref, (int, float)):
        if context is not None and context._evaluation_stack:
            try:
                current_ref_str = context._evaluation_stack[-1]
                cell = CellAddress.from_string(current_ref_str)
                if not cell.sheet:
                    cell.sheet = context.sheet
                return float(cell.row)
            except Exception as e:
                raise xlerrors.ValueExcelError("ROW: Unable to derive cell reference from evaluation context.") from e
        else:
            raise xlerrors.ValueExcelError("ROW expects a cell reference, not a numeric value.")

    raise xlerrors.ValueExcelError("ROW expects a cell reference, not the provided type.")

@xl.register()
def COLUMN(ref: func_xltypes.XlAnything, context=None) -> func_xltypes.XlNumber:
    from xlcalc.xltypes import XlReference
    """
    Returns the column number of the given cell reference.
    
    - If the argument is an XlReference (our wrapper), it extracts its CellAddress
      and returns the column number.
    - If the argument is a CellAddress or a string that parses as one, its column
      number is returned.
    - If the argument is a string that is not a proper cell reference, it is looked
      up as a defined name.
    - If the argument is numeric, we assume that the caller intended the reference
      to be that of the current cell (retrieved from the evaluation context).
    """
    if ref is None:
        raise xlerrors.ValueExcelError("COLUMN requires a cell reference argument.")

    # NEW: If ref is an instance of XlReference, extract its underlying CellAddress.
    if isinstance(ref, XlReference):
        cell = ref.get_address()
        if not cell.sheet:
            cell.sheet = context.sheet
        return float(col_letters_to_num(cell.column))

    # If ref is already a CellAddress, use it.
    if isinstance(ref, CellAddress):
        return float(col_letters_to_num(ref.column))

    # If ref is a string that looks like a cell reference.
    if isinstance(ref, str):
        if re.match(r"^\$?[A-Za-z]{1,3}\$?\d+$", ref):
            try:
                cell = CellAddress.from_string(ref)
                return float(col_letters_to_num(cell.column))
            except Exception as e:
                raise xlerrors.ValueExcelError(f"Invalid cell reference in COLUMN: {ref}") from e
        else:
            # Assume it's a defined name.
            if context is None:
                raise xlerrors.ValueExcelError("COLUMN cannot resolve a defined name without an evaluation context.")
            try:
                cell = context.model.resolve_defined_name(ref, context.sheet)
                return float(col_letters_to_num(cell.column))
            except Exception as e:
                raise xlerrors.ValueExcelError(f"Invalid cell reference or defined name in COLUMN: {ref}") from e

    # If ref is numeric, fallback to use the current cell reference from the evaluation stack.
    if isinstance(ref, (int, float)):
        if context is not None and context._evaluation_stack:
            try:
                current_ref_str = context._evaluation_stack[-1]
                cell = CellAddress.from_string(current_ref_str)
                if not cell.sheet:
                    cell.sheet = context.sheet
                return float(col_letters_to_num(cell.column))
            except Exception as e:
                raise xlerrors.ValueExcelError("COLUMN: Unable to derive cell reference from evaluation context.") from e
        else:
            raise xlerrors.ValueExcelError("COLUMN expects a cell reference, not a numeric value.")

    raise xlerrors.ValueExcelError("COLUMN expects a cell reference, not the provided type.")

@xl.register()
@xl.validate_args
def CHOOSE(
    index_num: func_xltypes.XlNumber,
    *values,
) -> func_xltypes.XlAnything:
    """
    Uses index_num (1-based) to return a value from the list of values.

    If index_num=1 => returns values[0].
    Raises ValueExcelError if index_num is not between 1 and 254 or exceeds the number of provided values.
    """
    if index_num <= 0 or index_num > 254:
        raise xlerrors.ValueExcelError(
            f"`index_num`={index_num} must be between 1 and 254."
        )
    if index_num > len(values):
        raise xlerrors.ValueExcelError(
            f"`index_num`={index_num} must not exceed the number of values={len(values)}"
        )

    idx = int(index_num) - 1
    return values[idx]

@xl.register()
#@xl.validate_args
def VLOOKUP(lookup_value, table_array, col_index_num, range_lookup=False, context=None):
    import numpy as np
    # At this point, thanks to the evaluator’s centralized dereferencing,
    # lookup_value is already the plain value (not an XlReference)
    col_index_num = int(col_index_num)
    if col_index_num < 1:
        raise xlerrors.ValueExcelError("col_index_num must be >= 1")
    arr = table_array.data  # a NumPy object array
    rows, cols = arr.shape
    if col_index_num > cols:
        raise xlerrors.ValueExcelError("col_index_num is greater than the number of columns in the table array")
    
    # Get the first column.
    first_col = arr[:, 0]
    
    # If the lookup value is numeric, ensure that the lookup table is numeric.
    if isinstance(lookup_value, (int, float)):
        # If the first element isn’t numeric, assume it’s a header row and drop it.
        try:
            float(first_col[0])
        except (ValueError, TypeError):
            arr = arr[1:, :]
            first_col = arr[:, 0]
        
        coerced = []
        for item in first_col:
            try:
                coerced.append(float(item))
            except (ValueError, TypeError):
                # Replace header or nonconvertible cells with NaN.
                coerced.append(np.nan)
        first_col = np.array(coerced)
    
    # Now perform the lookup.
    if range_lookup:
        idx = np.searchsorted(first_col, lookup_value, side='right') - 1
        if idx < 0:
            raise xlerrors.NaExcelError("lookup_value is smaller than all values in the first column.")
        row_idx = idx
    else:
        matches = np.where(first_col == lookup_value)[0]
        if len(matches) == 0:
            raise xlerrors.NaExcelError("lookup_value not found in the first column.")
        row_idx = matches[0]
    
    return arr[row_idx, col_index_num - 1]

@xl.register()
#@xl.validate_args
def HLOOKUP(lookup_value, table_array, row_index_num, range_lookup=False, context=None):
    import numpy as np
    from xlcalc import xlerrors

    row_index_num = int(row_index_num)
    if row_index_num < 1:
        raise xlerrors.ValueExcelError(f"row_index_num must be >= 1, got {row_index_num}")
    arr = table_array.data  # a NumPy object array with shape (rows, columns)
    rows, cols = arr.shape
    if row_index_num > rows:
        raise xlerrors.ValueExcelError(
            f"row_index_num={row_index_num} is greater than the number of rows in table_array ({rows})."
        )

    first_row = arr[0, :]

    # If the lookup value is numeric, make sure the lookup row is numeric.
    if isinstance(lookup_value, (int, float)):
        try:
            float(first_row[0])
        except (ValueError, TypeError):
            arr = arr[:, 1:]
            first_row = arr[0, :]
        coerced = []
        for item in first_row:
            try:
                coerced.append(float(item))
            except (ValueError, TypeError):
                coerced.append(np.nan)
        first_row = np.array(coerced)
    
    if range_lookup:
        idx = np.searchsorted(first_row, lookup_value, side='right') - 1
        if idx < 0:
            raise xlerrors.NaExcelError(
                f"lookup_value={lookup_value} is smaller than all values in the first row of table_array."
            )
        col_idx = idx
    else:
        matches = np.where(first_row == lookup_value)[0]
        if len(matches) == 0:
            raise xlerrors.NaExcelError(
                f"lookup_value={lookup_value} not found in the first row of table_array."
            )
        col_idx = matches[0]
    
    return arr[row_index_num - 1, col_idx]

@xl.register()
#@xl.validate_args
def MATCH(
    lookup_value: func_xltypes.XlAnything,
    lookup_array: func_xltypes.XlArray,
    match_type: func_xltypes.XlNumber = 1,
) -> func_xltypes.XlAnything:
    """
    Finds the 1-based position of 'lookup_value' in a 1D array.
    match_type=1 => ascending sorted approximate match
    match_type=0 => exact match
    match_type=-1 => descending approximate match

    If not found, raises a #N/A error.
    If the array is not sorted as required, also raises a #N/A error.
    """
    if lookup_array.shape[0] > 1 and lookup_array.shape[1] > 1:
        raise xlerrors.ValueExcelError("MATCH expects a 1D array (1 row or 1 column).")

    array_flat = lookup_array.flat

    mt = int(match_type)
    if mt == 1:
        sorted_asc = sorted(array_flat)
        if array_flat != sorted_asc:
            return xlerrors.NaExcelError("Values must be sorted ascending.")
        for i, val in enumerate(array_flat):
            if val == lookup_value:
                return i + 1
            if val > lookup_value:
                if i == 0:
                    return xlerrors.NaExcelError("No lesser value found.")
                return i
        return len(array_flat)

    if mt == -1:
        sorted_desc = sorted(array_flat, reverse=True)
        if array_flat != sorted_desc:
            return xlerrors.NaExcelError("Values must be sorted descending.")
        for i, val in enumerate(array_flat):
            if val == lookup_value:
                return i + 1
            if val < lookup_value:
                if i == 0:
                    return xlerrors.NaExcelError("No greater value found.")
                return i
        return len(array_flat)

    # match_type=0 exact
    for i, val in enumerate(array_flat):
        if val == lookup_value:
            return i + 1
    return xlerrors.NaExcelError("No match found.")
