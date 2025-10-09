## references.py
import re
from string import ascii_uppercase

def col_letters_to_num(col_letters: str) -> int:
    """Convert 'A'->1, 'B'->2, ..., 'AA'->27, etc."""
    result = 0
    for c in col_letters.upper():
        result = result * 26 + (ord(c) - ord('A') + 1)
    return result

def col_num_to_letters(col_num: int) -> str:
    """Convert 1->'A', 2->'B', 27->'AA', etc."""
    letters = []
    while col_num > 0:
        remainder = (col_num - 1) % 26
        letters.append(chr(remainder + ord('A')))
        col_num = (col_num - 1) // 26
    return "".join(reversed(letters))


class CellAddress:
    """
    Represents a single cell reference with optional absolute row/column.
    E.g. '$A1', 'A$1', '$AA$3', etc.
    (Sheet names are handled by RangeNode before calling from_string().)
    """

    # Now we ONLY parse something like '$A$1' or 'AA10' or 'A1'.
    ADDRESS_RE = re.compile(
        r"^(?P<col>\$?[A-Za-z]{1,3})(?P<row>\$?\d{1,6})$"
    )

    def __init__(self, sheet=None, column=None, row=None,
                 is_abs_col=False, is_abs_row=False):
        self.sheet = sheet
        self.column = column   # e.g. 'A', 'B', 'AA'
        self.row = row         # int
        self.is_abs_col = is_abs_col
        self.is_abs_row = is_abs_row

    @classmethod
    def from_string(cls, ref_str):
        ref_str = ref_str.strip()
        m = cls.ADDRESS_RE.match(ref_str)
        if not m:
            raise ValueError(f"Invalid cell reference: {ref_str}")

        col_part = m.group("col")   # e.g. "$AA" or "B"
        row_part = m.group("row")   # e.g. "$3" or "10"

        # Check absolute flags
        is_abs_col = col_part.startswith('$')
        is_abs_row = row_part.startswith('$')

        # Strip '$' from the actual column & row strings
        col_letters = col_part.lstrip('$').upper()
        row_digits = row_part.lstrip('$')

        #print("DEBUG -> col_letters=", col_letters, "row_digits=", row_digits)
        obj = cls(
            sheet=None,  # sheet is assigned later in RangeNode, if any
            column=col_letters,
            row=int(row_digits),
            is_abs_col=is_abs_col,
            is_abs_row=is_abs_row
        )
        #print("DEBUG -> returning CellAddress:", obj)
        return obj

    def canonical_address(self) -> str:
        """
        Return a string like 'A1' with no '$', or 'Sheet1!A1' if we also store .sheet
        but ignoring absolute. Typically used as a dictionary key.
        """
        base = f"{self.column}{self.row}"
        if self.sheet:
            return f"{self.sheet}!{base}"
        return base

    def __eq__(self, other):
        if isinstance(other, CellAddress):
            return self.canonical_address() == other.canonical_address()
        return False

    def __hash__(self):
        return hash(self.canonical_address())
    
    def to_string(self, include_sheet=True):
        """
        Return e.g. 'Sheet1!$A$1' if sheet is 'Sheet1', or '$A$1' if no sheet.
        """
        parts = []
        if include_sheet and self.sheet:
            # if sheet has spaces or '!' then we wrap it in quotes
            if " " in self.sheet or "!" in self.sheet:
                parts.append(f"'{self.sheet}'!")
            else:
                parts.append(f"{self.sheet}!")
        if self.is_abs_col:
            parts.append(f"${self.column}")
        else:
            parts.append(f"{self.column}")
        if self.is_abs_row:
            parts.append(f"${self.row}")
        else:
            parts.append(f"{self.row}")
        return "".join(parts)

    def plain_reference(self):
        """
        Return the cell reference as a plain string (without sheet information)
        that can be parsed by from_string(). For example, returns 'D$28'.
        """
        return self.to_string(include_sheet=False)

    def offset(self, row_offset, col_offset):
        """
        Shift row/column by offsets, ignoring whichever dimension is absolute.
        E.g. if is_abs_col=True, col won't shift, etc.
        """
        c_num = col_letters_to_num(self.column)
        r_num = self.row

        if not self.is_abs_col:
            c_num += col_offset
        if not self.is_abs_row:
            r_num += row_offset

        new_col = col_num_to_letters(c_num)
        return CellAddress(
            sheet=self.sheet,
            column=new_col,
            row=r_num,
            is_abs_col=self.is_abs_col,
            is_abs_row=self.is_abs_row
        )

    def __repr__(self):
        return f"<CellAddress {self.to_string()}>"
