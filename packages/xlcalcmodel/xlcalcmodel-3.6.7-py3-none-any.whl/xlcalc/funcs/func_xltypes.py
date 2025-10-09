# func_xltypes.py
import datetime
import math
import numpy as np
from typing import Optional, Union, NewType

from . import xlerrors

########################################
# Registration for "native -> ExcelType"
########################################
NATIVE_TO_XLTYPE = {}

def register(cls):
    """
    Decorator for typed classes so that for each 'native_type' they handle,
    we store an entry in NATIVE_TO_XLTYPE.
    Example: Number can handle int,float => we map {int:Number, float:Number}.
    """
    for native_type in cls.native_types:
        NATIVE_TO_XLTYPE[native_type] = cls
    return cls


########################################
# Base "ExcelType"
########################################
class ExcelType:
    """
    Base for typed objects like Number, Text, Boolean, DateTime, Blank, etc.
    Provides operator overloading to mimic Excel arithmetic/comparisons.
    """
    __slots__ = ('value',)
    native_types = ()    # e.g. (int,float) for Number
    sort_precedence = 0  # used for text>number or number>boolean, etc.

    def __new__(cls, value):
        inst = super().__new__(cls)
        # Basic assertion. If you see an error, might be because you're passing
        # in e.g. float => Number => but forgot to register float for Number.
        assert isinstance(value, cls.native_types), f"{value} not in {cls.native_types}"
        inst.value = value
        return inst

    @classmethod
    def cast(cls, value):
        """
        Force 'value' to become an instance of 'cls'.
        If 'value' is already an ExcelType, we call e.g. value.__Number__() if cls=Number.
        If 'value' is a plain Python type, we see if there's a known mapping in NATIVE_TO_XLTYPE.
        """
        if isinstance(value, cls):
            return value

        if not isinstance(value, ExcelType):
            # e.g. 'float' => NATIVE_TO_XLTYPE[float] => Number
            cast_cls = NATIVE_TO_XLTYPE.get(type(value))
            if not cast_cls:
                raise xlerrors.ValueExcelError(f"Unknown type {type(value)} => {value}")
            value = cast_cls(value)
        # now 'value' is an ExcelType
        return getattr(value, f"__{cls.__name__}__")()

    @classmethod
    def cast_from_native(cls, value):
        """
        If 'value' is a Python type (int,float,str,...) or another ExcelType,
        produce an instance of 'cls' or error.
        If it's an ExcelError, pass it through.
        """
        if isinstance(value, xlerrors.ExcelError):
            return value
        if isinstance(value, ExcelType):
            return value
        cast_cls = NATIVE_TO_XLTYPE.get(type(value))
        if cast_cls:
            return cast_cls(value)
        raise xlerrors.ValueExcelError(f"Cannot cast type {type(value)} => {value}")

    def _sort_key(self, other):
        # For <, >, etc. we'll compare (sort_precedence, self.value)
        return (self.sort_precedence, self.value)

    ###############
    # Arithmetic
    ###############
    def __add__(self, other):
        return Number( Number.cast(self).value + Number.cast(other).value )

    def __sub__(self, other):
        return Number( Number.cast(self).value - Number.cast(other).value )

    def __mul__(self, other):
        return Number( Number.cast(self).value * Number.cast(other).value )

    def __truediv__(self, other):
        den = float(Number.cast(other))
        if den == 0:
            raise xlerrors.DivZeroExcelError()
        return Number(float(Number.cast(self)) / den)

    def __pow__(self, other):
        return Number( Number.cast(self).value ** Number.cast(other).value )

    ###############
    # Logical
    ###############
    def __and__(self, other):
        return Boolean(bool(self) and bool(other))

    def __or__(self, other):
        return Boolean(bool(self) or bool(other))
        
    ###############
    # R-ops (commutative vs. non-commutative)
    ###############
    __radd__ = __add__
    __rmul__ = __mul__
    __rpow__ = __pow__
    # For AND/OR we can keep the same references
    __rand__ = __and__
    __ror__ = __or__

    # NON-commutative => must define properly
    def __rsub__(self, other):
        """
        For 'other - self':
        e.g.  5 - ExcelType(4) => (5) - (4) => +1
        """
        left_val = float(Number.cast_from_native(other))
        right_val = float(Number.cast_from_native(self))
        return Number(left_val - right_val)

    def __rtruediv__(self, other):
        """
        For 'other / self':
        e.g.  10 / ExcelType(2) => 10 / 2 => +5
        """
        numerator = float(Number.cast_from_native(other))
        denominator = float(Number.cast_from_native(self))
        if denominator == 0:
            raise xlerrors.DivZeroExcelError()
        return Number(numerator / denominator)

    ###############
    # Comparisons
    ###############
    def __lt__(self, other):
        o = ExcelType.cast_from_native(other)
        return Boolean(self._sort_key(o) < o._sort_key(self))

    def __le__(self, other):
        o = ExcelType.cast_from_native(other)
        return Boolean(self._sort_key(o) <= o._sort_key(self))

    def __eq__(self, other):
        o = ExcelType.cast_from_native(other)
        return Boolean(self._sort_key(o) == o._sort_key(self))

    def __ne__(self, other):
        o = ExcelType.cast_from_native(other)
        return Boolean(self._sort_key(o) != o._sort_key(self))

    def __gt__(self, other):
        o = ExcelType.cast_from_native(other)
        return Boolean(self._sort_key(o) > o._sort_key(self))

    def __ge__(self, other):
        o = ExcelType.cast_from_native(other)
        return Boolean(self._sort_key(o) >= o._sort_key(self))

    ###############
    # Casting
    ###############
    def __int__(self):
        return int(float(self.value))

    def __float__(self):
        try:
            return float(self.value)
        except:
            raise xlerrors.ValueExcelError(f"Cannot float-cast {self.value}")

    def __bool__(self):
        return bool(self.value)

    def __number__(self):
        """Used in __Number__ => override if needed"""
        return float(self.value)

    def __datetime__(self):
        """Override in DateTime"""
        raise NotImplementedError

    def __Number__(self):
        return Number(self.__number__())

    def __Text__(self):
        return Text(str(self.value))

    def __Boolean__(self):
        return Boolean(bool(self.value))

    def __DateTime__(self):
        raise xlerrors.ValueExcelError("Cannot interpret as DateTime")

    def __Blank__(self):
        return Blank()

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.value!r}>"


@register
class Number(ExcelType):
    native_types = (int, float)

    @classmethod
    def is_type(cls, value):
        return isinstance(value, cls)

    def __mod__(self, other):
        return Number(self.value % Number.cast(other).value)
    __rmod__ = __mod__

    def __neg__(self):
        return Number(-self.value)

    def __abs__(self):
        return Number(abs(self.value))

    def __number__(self):
        return float(self.value)

    def __datetime__(self):
        # if you want to interpret float as date, do so with an epoch approach
        raise xlerrors.ValueExcelError("Number->datetime not supported by default")


@register
class Text(ExcelType):
    native_types = (str,)
    sort_precedence = 1

    def __number__(self):
        # attempt to parse as float
        try:
            return float(self.value)
        except:
            raise xlerrors.ValueExcelError(f"Cannot parse '{self.value}' as number.")

    def __datetime__(self):
        # skip for performance or implement parse
        raise xlerrors.ValueExcelError(f"Cannot parse '{self.value}' as date/time")


@register
class Boolean(ExcelType):
    native_types = (bool,)
    sort_precedence = 2

    def __number__(self):
        return 1.0 if self.value else 0.0

    def __datetime__(self):
        # if you want True => some date, False => another => skip for performance
        raise xlerrors.ValueExcelError("Boolean->datetime not supported")


@register
class DateTime(ExcelType):
    native_types = (datetime.datetime,)

    def __number__(self):
        # if you want to do datetime->float, implement it
        raise xlerrors.ValueExcelError("DateTime->number not implemented")

    def __DateTime__(self):
        return self


@register
class Blank(ExcelType):
    native_types = (type(None),)

    @classmethod
    def is_blank(cls, value):
        # if value == '':
        #     return True
        return (value is None) or isinstance(value, cls)

    def __new__(cls, value=None):
        return super().__new__(cls, None)

    def __bool__(self):
        return False

    def __number__(self):
        return 0.0

    def __str__(self):
        return ""

    def __DateTime__(self):
        raise xlerrors.ValueExcelError("Blank->datetime not supported")


###########################
# NumPy-based XlArray
###########################
class Array:
    """
    2D array stored in a NumPy 'object' array. Each cell can hold any Python object
    or ExcelType. Provides cast_to_numbers, cast_to_booleans, etc.
    """
    __slots__ = ('data',)

    def __init__(self, data):
        if not isinstance(data, np.ndarray):
            data = np.array(data, dtype=object)
        # ensure 2D
        if data.ndim == 1:
            data = data.reshape((data.shape[0], 1))
        if data.dtype != object:
            data = data.astype(object)
        self.data = data

    @property
    def shape(self):
        return self.data.shape

    @property
    def values(self):
        """Return a list-of-lists version if needed."""
        return self.data.tolist()

    @property
    def flat(self):
        """Flatten into a python list of items."""
        return self.data.ravel(order='C').tolist()

    def cast_to_numbers(self):
        new_data = np.empty(self.data.shape, dtype=object)
        for idx, val in np.ndenumerate(self.data):
            try:
                new_data[idx] = Number.cast_from_native(val)
            except xlerrors.ExcelError:
                new_data[idx] = Number(0.0)
        arr2 = Array.__new__(Array)
        arr2.data = new_data
        return arr2

    def cast_to_booleans(self):
        new_data = np.empty(self.data.shape, dtype=object)
        for idx, val in np.ndenumerate(self.data):
            try:
                new_data[idx] = Boolean.cast_from_native(val)
            except xlerrors.ExcelError:
                new_data[idx] = Boolean(False)
        arr2 = Array.__new__(Array)
        arr2.data = new_data
        return arr2

    def cast_to_texts(self):
        new_data = np.empty(self.data.shape, dtype=object)
        for idx, val in np.ndenumerate(self.data):
            try:
                new_data[idx] = Text.cast_from_native(val)
            except xlerrors.ExcelError:
                new_data[idx] = Text("")
        arr2 = Array.__new__(Array)
        arr2.data = new_data
        return arr2

    def __repr__(self):
        return f"<Array shape={self.shape}, data={self.data}>"

    @classmethod
    def cast(cls, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, np.ndarray):
            if value.dtype != object:
                value = value.astype(object)
            arr = Array.__new__(Array)
            arr.data = value
            return arr
        # single item => wrap
        if not isinstance(value, (list, tuple)):
            value = [[value]]
        return cls(value)


###########################
# Expression
###########################
class Expr:
    """
    Delayed expression, if you want.
    """
    def __init__(self, callable, args=(), kwargs={}, **info):
        self.callable = callable
        self.args = args
        self.kwargs = kwargs.copy()
        for k, v in info.items():
            setattr(self, k, v)

    @classmethod
    def cast(cls, value):
        if isinstance(value, cls):
            return value
        return ValueExpr(value)

    def __call__(self):
        return self.callable(*self.args, **self.kwargs)


def ValueExpr(value):
    return Expr(lambda: value, value=value)


###########################
# The "Xl" NewTypes
###########################
_Anything = Optional[Union[
    int, float, bool, str, datetime.datetime,
    Number, Text, Boolean, DateTime, Blank, xlerrors.ExcelError
]]

XlNumber = NewType('XlNumber', _Anything)
XlText = NewType('XlText', _Anything)
XlBoolean = NewType('XlBoolean', _Anything)
XlDateTime = NewType('XlDateTime', _Anything)
XlBlank = NewType('XlBlank', _Anything)
#XlArray = NewType('XlArray', Union[_Anything, list, Array, np.ndarray])
XlArray = Array
XlExpr = NewType('XlExpr', Union[_Anything, Expr])

# XlAnything for open-ended returns:
XlAnything = Union[XlNumber, XlText, XlBoolean, XlDateTime, XlBlank, XlArray]


class Unused:
    """If a function can omit an optional param vs. passing blank, we can differentiate."""
    pass


UNUSED = Unused()
