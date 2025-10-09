# xl.py
import functools
import inspect
import typing

# Make sure these imports match your file structure
from . import func_xltypes, xlerrors
from xlcalc.xltypes import XlArray, XlReference

COMPATIBILITY = 'EXCEL'
CELL_CHARACTER_LIMIT = 32767

# Maps each "Xl*" annotation type to a "cast" function that coerces input
# (like a Python float) into the right typed XlObject (like XlNumber).
TYPE_TO_CAST = {
    func_xltypes.XlNumber: func_xltypes.Number.cast,
    func_xltypes.XlText: func_xltypes.Text.cast,
    func_xltypes.XlBoolean: func_xltypes.Boolean.cast,
    func_xltypes.XlDateTime: func_xltypes.DateTime.cast,
    func_xltypes.XlArray: func_xltypes.Array.cast,
    func_xltypes.XlExpr: func_xltypes.Expr.cast,
    func_xltypes.XlAnything: func_xltypes.ExcelType.cast_from_native,
}


##################################
# A registry for "Excel" Functions
##################################
class Functions(dict):
    """
    A custom dictionary to store function_name -> function_object,
    with the ability to do `FUNCTIONS.register(...)` or `@register(...)`.
    """

    def register(self, func, name=None):
        if name is None:
            name = func.__name__
        self[name] = func

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


FUNCTIONS = Functions()


def register(name=None):
    """
    Decorator to register a function into the global FUNCTIONS registry.
    Usage:
        @register()
        def MYFUNC(...):
            ...
    """
    def registerFunction(func):
        FUNCTIONS.register(func, name)
        return func
    return registerFunction


##################################
# Validating arguments using hints
##################################
def _validate(vtype, val, name):
    """
    Attempt to coerce 'val' into the typed object or structure
    indicated by 'vtype' (one of the Xl classes, or Union, etc.).
    """
    cast = TYPE_TO_CAST.get(vtype, None)
    if cast is not None:
        return cast(val)

    # If the annotation is e.g. List[XlNumber] or Tuple[XlNumber], we flatten the input
    # and validate each item.
    origin = getattr(vtype, '__origin__', None)
    if origin in [list, tuple]:
        itype = vtype.__args__[0]
        if itype != func_xltypes.XlArray:
            val = flatten(val)
        validated = [
            _safe_validate(itype, item, name)
            for item in val if item is not None
        ]
        if origin is list:
            return validated  # return a list
        else:
            return tuple(validated)

    # If it's a Union[...] type, try each possibility.
    if getattr(vtype, '__origin__', None) == typing.Union:
        for stype in vtype.__args__:
            try:
                return _validate(stype, val, name)
            except xlerrors.ExcelError:
                pass
        raise xlerrors.ValueExcelError(val)

    # Fallback: if we can’t find a cast, just return 'val' as is.
    return val

def _safe_validate(vtype, val, name):
    """
    A helper that tries _validate, catching ExcelError. If it fails,
    we skip that item.
    """
    try:
        return _validate(vtype, val, name)
    except xlerrors.ExcelError:
        return None

def validate_args(func):
    """
    Decorator that uses the function signature to coerce input arguments
    and the return value to the expected Excel type.

    In our enhanced ecosystem we want to pass through any argument that is already
    an XlReference, an XlArray, or a list. (Also, if the parameter is a varargs
    parameter, we leave it untouched.)
    """
    @functools.wraps(func)
    def wrapper(*args, **kw):
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kw)

        # Process input parameters:
        for pname, value in list(bound.arguments.items()):
            param = sig.parameters[pname]
            # For varargs (i.e. *args), do not try to coerce the entire tuple.
            if param.kind == param.VAR_POSITIONAL:
                continue

            # Immediately propagate ExcelError values.
            if isinstance(value, xlerrors.ExcelError):
                return value

            # If the value is already one of our special types, do nothing.
            if isinstance(value, (XlReference, XlArray)) or isinstance(value, list):
                continue

            try:
                bound.arguments[pname] = _validate(param.annotation, value, pname)
            except xlerrors.ExcelError as err:
                return err

        # Call the original function.
        try:
            res = func(*bound.args, **bound.kwargs)
        except xlerrors.ExcelError as err:
            return err

        # Process the return value:
        if isinstance(res, (XlReference, XlArray)) or isinstance(res, list):
            return res
        return _validate(sig.return_annotation, res, 'return')

    return wrapper

##########################
# Flatten / length helpers
##########################
def flatten(values):
    """
    Recursively flatten an XlArray or nested lists/tuples into a 1D list.
    """
    # If the entire argument is an XlArray, replace 'values' with its .flat
    if isinstance(values, func_xltypes.Array):
        values = values.flat  # .flat is typically a python list

    out = []
    for val in values:
        if isinstance(val, func_xltypes.Array):
            # Recursively flatten the array's .flat
            out.extend(flatten(val.flat))
        elif isinstance(val, (list, tuple)):
            # If it's another nested list/tuple, recurse
            out.extend(flatten(val))
        else:
            # Base case: a single item (string, number, etc.)
            out.append(val)
    return out



def length(values):
    """Return the length of a fully flattened list/array."""
    return len(flatten(values))
