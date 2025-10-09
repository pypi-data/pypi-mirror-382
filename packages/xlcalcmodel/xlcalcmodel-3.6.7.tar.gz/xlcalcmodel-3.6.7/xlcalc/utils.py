# xlutils.py

import re
from openpyxl.utils.cell import range_boundaries, get_column_letter

MAX_COL = 18278       # openpyxl logic, up to "ZZZ..."
MAX_ROW = 1048576     # Excel's max rows

def parse_xl_range(rng_str):
    """
    Parse partial references like 'A:A', '1:1', 'A:C', or 'A1:B5' using
    openpyxl's range_boundaries(). Returns (min_col, min_row, max_col, max_row)
    with defaults if missing.
    """
    min_col, min_row, max_col, max_row = range_boundaries(rng_str)
    # If it's an unbound reference like 'A:A' => min_row=None, max_row=None
    min_col = min_col or 1
    min_row = min_row or 1
    max_col = max_col or MAX_COL
    max_row = max_row or MAX_ROW
    return min_col, min_row, max_col, max_row
