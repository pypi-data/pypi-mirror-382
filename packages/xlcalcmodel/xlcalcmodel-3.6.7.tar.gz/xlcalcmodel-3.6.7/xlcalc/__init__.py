from .funcs.xl import FUNCTIONS, register
from .funcs.xlerrors import *  
from .funcs.func_xltypes import *
from .model import Model
from .evaluator import EvalContext
from xlcalc import dependency

# Register all functions
from .funcs import ( 
    date_funcs,
    date_utils,
    engineering_funcs,
    financial_funcs,
    information_funcs,
    logical_funcs,
    lookup,
    math_funcs,
    statistics,
    text
)

name = "xlcalc"
