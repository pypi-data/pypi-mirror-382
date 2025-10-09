"""Utilities for compiling cell formulas to Python callables."""

from __future__ import annotations

import logging
import textwrap
from typing import Any
import numpy as np

from .references import CellAddress
from .parser import (
    OperandNode,
    RangeNode,
    OperatorNode,
    FunctionNode,
    group_addresses_and_fetch,
    PREFIX_OP_TO_FUNC,
    POSTFIX_OP_TO_FUNC,
    INFIX_OP_TO_FUNC,
)
from .funcs.xl import FUNCTIONS
from .xltypes import XlReference, XlArray


##logger = logging.getLogger(__name__)
##
##compiled_logger = logging.getLogger("xlcalc.compiled")
##if not compiled_logger.handlers:
##    handler = logging.FileHandler("compiled_functions.log")
##    formatter = logging.Formatter("%(asctime)s - %(message)s")
##    handler.setFormatter(formatter)
##    compiled_logger.addHandler(handler)
##    compiled_logger.setLevel(logging.INFO)


def is_single_cell_reference(xlref: XlReference) -> bool:
    addr = xlref.get_address()
    return ":" not in str(addr)


def resolve_operand(context, val):
    if isinstance(val, XlReference):
        if is_single_cell_reference(val):
            cell = context.model.get_cell(val.get_address())
            return context.eval_cell_value(cell)
        return val.get_value(context)
    elif isinstance(val, (list, np.ndarray)) and not isinstance(val, XlArray):
        return XlArray(np.array(val))
    return val


def eval_range(context, rng_str: str):
    """Replicate RangeNode evaluation for compiled formulas."""
    if "!" in rng_str:
        sheet_part, rng_part = rng_str.split("!", 1)
        sheet_name = sheet_part.strip().strip("'")
    else:
        sheet_name = context.sheet
        rng_part = rng_str

    if ":" in rng_part:
        addrs = context.model.resolve_range(sheet_name, rng_part)
        return group_addresses_and_fetch(context, addrs)
    else:
        addr_obj = CellAddress.from_string(rng_part)
        if not addr_obj.sheet:
            addr_obj.sheet = sheet_name
        return XlReference(addr_obj)

def _node_to_expr(node: Any, sheet_name: str, model) -> str:
    """Convert a parsed AST node to a Python expression string."""
    if isinstance(node, OperandNode):
        val = node.tvalue
        try:
            return repr(float(val))
        except Exception:
            return repr(val)

    if isinstance(node, RangeNode):
        rng_str = node.tvalue
        if "!" in rng_str:
            sheet_part, rng_part = rng_str.split("!", 1)
            rng_sheet = sheet_part.strip().strip("'")
        else:
            rng_sheet = sheet_name
            rng_part = rng_str

        if ":" in rng_part:
            addrs = model.resolve_range(rng_sheet, rng_part)
            addr_code = "[" + ", ".join(
                f"CellAddress(sheet={repr(a.sheet)}, column={repr(a.column)}, row={a.row})"
                for a in addrs
            ) + "]"
            return f"group_addresses_and_fetch(context, {addr_code})"
        else:
            addr = CellAddress.from_string(rng_part)
            if not addr.sheet:
                addr.sheet = rng_sheet
            addr_code = (
                f"CellAddress(sheet={repr(addr.sheet)}, column={repr(addr.column)}, row={addr.row})"
            )
            return f"XlReference({addr_code})"

    if isinstance(node, OperatorNode):
        if node.ttype == "OP_PREFIX":
            operand = _node_to_expr(node.right, sheet_name, model)
            return (
                f"PREFIX_OP_TO_FUNC[{repr(node.tvalue)}](resolve_operand(context, {operand}))"
            )
        if node.ttype == "OP_POSTFIX":
            operand = _node_to_expr(node.left, sheet_name, model)
            return (
                f"POSTFIX_OP_TO_FUNC[{repr(node.tvalue)}](resolve_operand(context, {operand}))"
            )
        if node.ttype == "OP_INFIX":
            left = _node_to_expr(node.left, sheet_name, model)
            right = _node_to_expr(node.right, sheet_name, model)
            return (
                f"INFIX_OP_TO_FUNC[{repr(node.tvalue)}](resolve_operand(context, {left}), resolve_operand(context, {right}))"
            )

    if isinstance(node, FunctionNode):
        args = ", ".join(_node_to_expr(a, sheet_name, model) for a in node.args)
        return f"context.call_function({repr(node.tvalue)}, [{args}])"

    raise TypeError(f"Unsupported node type: {type(node)!r}")

def compile_cell(cell, model) -> None:
    """Attach a compiled callable to the cell for faster evaluation."""
    if not getattr(cell, "parsed_ast", None):
        return
    sheet = cell.address_obj.sheet or "Sheet1"
    expr = _node_to_expr(cell.parsed_ast, sheet, model)
    code = "def compiled_func(context):\n    return " + expr
##    compiled_logger.info(
##        "Compiled function for %s:\n%s",
##        cell.address_obj.to_string(),
##        textwrap.dedent(code),
##    )
    ns = {
        "eval_range": eval_range,
        "PREFIX_OP_TO_FUNC": PREFIX_OP_TO_FUNC,
        "POSTFIX_OP_TO_FUNC": POSTFIX_OP_TO_FUNC,
        "INFIX_OP_TO_FUNC": INFIX_OP_TO_FUNC,
        "FUNCTIONS": FUNCTIONS,
        "CellAddress": CellAddress,
        "group_addresses_and_fetch": group_addresses_and_fetch,
        "XlReference": XlReference,
        "XlArray": XlArray,
        "np": np,
        "resolve_operand": resolve_operand,
    }
    exec(textwrap.dedent(code), ns)
    cell.compiled_func = ns["compiled_func"]
