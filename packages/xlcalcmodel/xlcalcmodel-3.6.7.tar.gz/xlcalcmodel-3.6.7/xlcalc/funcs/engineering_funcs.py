"""
engineering_funcs.py

Implements Excel-like base conversion functions:
  DEC2BIN, DEC2OCT, DEC2HEX,
  BIN2DEC, BIN2OCT, BIN2HEX,
  OCT2DEC, OCT2BIN, OCT2HEX,
  HEX2DEC, HEX2BIN, HEX2OCT.
"""

from typing import Literal, Optional, Union

# Instead of "from . import xl", import your xlregister decorator.
from . import xl, xlerrors, func_xltypes
from . import func_xltypes
from .func_xltypes import UNUSED, Unused
from .xlerrors import NumExcelError, ValueExcelError

# We'll represent 'dec' with a string, but bin, oct, hex as built-in references:
dec = "dec"
Base = Literal[bin, dec, oct, hex]

PERMITTED_DIGITS = {
    bin: set("01"),
    oct: set("01234567"),
    hex: set("0123456789ABCDEFabcdef"),
}

# Maximum bit widths for each base (for 2's-complement or sign extension).
BIT_WIDTHS = {
    bin: 10,
    oct: 30,
    hex: 40,
}

BASE_NUMBERS = {
    bin: 2,
    oct: 8,
    hex: 16,
}

# BOUNDS used for verifying input range (Excel constraints).
BOUNDS = {
    frozenset([bin, oct]): 2 ** 9,
    frozenset([bin, dec]): 2 ** 9,
    frozenset([bin, hex]): 2 ** 9,
    frozenset([oct, dec]): 2 ** 29,
    frozenset([oct, hex]): 2 ** 29,
    frozenset([dec, hex]): 2 ** 39,
}

def handle_places(
    places: Union[Unused, func_xltypes.XlAnything]
) -> Optional[int]:
    """
    Handle the optional 'places' argument in functions like DEC2BIN(..., places).
    Ensures it's an integer between 1 and 10, or raises an error if invalid.
    """
    if places is UNUSED:
        return None

    if isinstance(places, func_xltypes.Boolean):
        # Excel typically doesn't allow booleans here.
        raise ValueExcelError("The 'places' argument cannot be a boolean.")

    places = int(places)  # Convert from XlNumber or text to int
    if not (1 <= places <= 10):
        raise NumExcelError("The number of places must be between 1 and 10.")

    return places

def handle_number(number: func_xltypes.XlAnything, origin) -> Union[int, str]:
    """
    Interprets 'number' in the given 'origin' base (dec, bin, oct, hex).
    Returns either an integer (if origin='dec') or a string (if origin != 'dec').
    Raises NumExcelError/ValueExcelError if invalid.
    """
    if isinstance(number, func_xltypes.Boolean):
        raise ValueExcelError("The number cannot be a boolean.")

    if origin == dec:
      # If origin is decimal, parse as int. Catch invalid strings => #VALUE!
      try:
          return int(number)
      except (ValueError, TypeError):
          raise ValueExcelError("Cannot parse as a decimal number.")

    # Otherwise, we expect 'number' to be a string or something that can be cast
    # to text representing a base-specified number.
    if isinstance(number, func_xltypes.Blank):
        as_str = "0"
    elif isinstance(number, func_xltypes.Number):
        # Must be integral if user typed a float.
        if number.value != int(number.value):
            raise NumExcelError("Number is not an integer (for non-decimal base).")
        as_str = str(int(number.value))
    elif isinstance(number, func_xltypes.Text):
        as_str = str(number.value) if number.value else "0"
    else:
        # If some unknown type, attempt str conversion:
        as_str = str(number)

    if len(as_str) > 10:
        # Excel enforces a limit of 10 digits for binary/oct/hex inputs.
        raise NumExcelError("Input string too long.")

    # Check for invalid characters vs the permitted digits for that base.
    if set(as_str) - PERMITTED_DIGITS[origin]:
        raise NumExcelError("Invalid characters for this base.")

    return as_str

def pad_zeroes(string: str, was_negative: bool, places: Optional[int]) -> str:
    """
    If 'places' was specified, zero-pad 'string' to that length.
    'was_negative' affects 2's-complement handling for sign extension.
    """
    if places is None:
        return string

    # If the user wants N places, we must not exceed that length.
    # If was_negative is True, we allow an extra digit for sign. (Excel approach)
    desired_length = len(string) if was_negative else places

    if desired_length < len(string):
        raise NumExcelError("Resulting string is longer than the desired length.")

    return string.zfill(desired_length)

def conversion(number: Union[int, str], origin, destination, places):
    """
    Core logic: Convert 'number' from 'origin' base to 'destination' base,
    applying Excel constraints (2's-complement, bit widths, etc.).
    """
    # Step 1: Convert from origin base to an integer 'value'.
    if origin == dec:
        # 'number' is already an int in decimal
        value = number
    else:
        # Convert string in base -> int
        as_int = int(number, BASE_NUMBERS[origin])

        # 2's-complement style sign extension, mask by BIT_WIDTHS:
        mask = 1 << (BIT_WIDTHS[origin] - 1)
        value = (as_int & ~mask) - (as_int & mask)

    # Step 2: Check bounds for the origin->destination pair
    bound = BOUNDS[frozenset([origin, destination])]
    if not (-bound <= value < bound):
        raise NumExcelError("The input number is out of bounds.")

    # Step 3: If destination is decimal => just return int
    if destination == dec:
        return value

    # Step 4: 2's-complement handling for negative
    was_negative = value < 0
    if was_negative:
        value += 1 << BIT_WIDTHS[destination]

    # Step 5: Convert int -> destination base string
    result = destination(value)[2:].upper()

    # Step 6: Possibly zero-pad
    return pad_zeroes(result, was_negative, places)

def convert_bases(number, origin, destination, places=None):
    """
    High-level wrapper for base conversions.
    - 'places' may be None or UNUSED => no fixed width.
    - 'origin' and 'destination' can be dec, bin, oct, hex.
    Returns either a string (for bin/oct/hex) or int (for dec).
    """
    # 1) If places is provided, validate it:
    if places is not None:
        places = handle_places(places)

    # 2) Handle 'number' in the given origin base. This yields either int or str.
    number = handle_number(number, origin)

    # 3) Convert from origin -> destination base.
    return conversion(number, origin, destination, places)

#
# Excel function wrappers
#

@xl.register()
@xl.validate_args
def DEC2BIN(
    number: func_xltypes.XlAnything,
    places: func_xltypes.XlAnything = UNUSED
) -> func_xltypes.XlText:
    return convert_bases(number, dec, bin, places)

@xl.register()
@xl.validate_args
def DEC2OCT(
    number: func_xltypes.XlAnything,
    places: func_xltypes.XlAnything = UNUSED
) -> func_xltypes.XlText:
    return convert_bases(number, dec, oct, places)

@xl.register()
@xl.validate_args
def DEC2HEX(
    number: func_xltypes.XlAnything,
    places: func_xltypes.XlAnything = UNUSED
) -> func_xltypes.XlText:
    return convert_bases(number, dec, hex, places)


@xl.register()
@xl.validate_args
def BIN2DEC(
    number: func_xltypes.XlAnything
) -> func_xltypes.XlNumber:
    return convert_bases(number, bin, dec)

@xl.register()
@xl.validate_args
def BIN2OCT(
    number: func_xltypes.XlAnything,
    places: func_xltypes.XlAnything = UNUSED
) -> func_xltypes.XlText:
    return convert_bases(number, bin, oct, places)

@xl.register()
@xl.validate_args
def BIN2HEX(
    number: func_xltypes.XlAnything,
    places: func_xltypes.XlAnything = UNUSED
) -> func_xltypes.XlText:
    return convert_bases(number, bin, hex, places)


@xl.register()
@xl.validate_args
def OCT2DEC(
    number: func_xltypes.XlAnything
) -> func_xltypes.XlNumber:
    return convert_bases(number, oct, dec)

@xl.register()
@xl.validate_args
def OCT2BIN(
    number: func_xltypes.XlAnything,
    places: func_xltypes.XlAnything = UNUSED
) -> func_xltypes.XlText:
    return convert_bases(number, oct, bin, places)

@xl.register()
@xl.validate_args
def OCT2HEX(
    number: func_xltypes.XlAnything,
    places: func_xltypes.XlAnything = UNUSED
) -> func_xltypes.XlText:
    return convert_bases(number, oct, hex, places)


@xl.register()
@xl.validate_args
def HEX2DEC(
    number: func_xltypes.XlAnything
) -> func_xltypes.XlNumber:
    return convert_bases(number, hex, dec)

@xl.register()
@xl.validate_args
def HEX2BIN(
    number: func_xltypes.XlAnything,
    places: func_xltypes.XlAnything = UNUSED
) -> func_xltypes.XlText:
    return convert_bases(number, hex, bin, places)

@xl.register()
@xl.validate_args
def HEX2OCT(
    number: func_xltypes.XlAnything,
    places: func_xltypes.XlAnything = UNUSED
) -> func_xltypes.XlText:
    return convert_bases(number, hex, oct, places)

