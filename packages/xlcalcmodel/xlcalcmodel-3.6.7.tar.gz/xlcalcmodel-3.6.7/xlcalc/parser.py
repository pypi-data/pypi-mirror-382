# parser.py
import re
from .references import CellAddress
from .xltypes import XlReference, XlArray
import logging
logger = logging.getLogger(__name__)

class Token:
    def __init__(self, ttype, tvalue, tsubtype=""):
        self.ttype = ttype
        self.tvalue = tvalue
        self.tsubtype = tsubtype

    def __repr__(self):
        return f"<Token {self.ttype} {self.tvalue!r}>"

########################################################################
# 1) SIMPLIFIED REF_PATTERN: no optional sheet logic in this regex
########################################################################
REF_PATTERN = (
    # 1) Optional quoted or unquoted sheet name, followed by '!', then cell/range
    r"(?:'[^']+'|[A-Za-z0-9_]+)!\$?[A-Za-z]{1,3}\$?[0-9]{1,6}"
    r"(?:\:\$?[A-Za-z]{1,3}\$?[0-9]{1,6})?"
    "|"  
    # 2) Or just the cell reference alone (no '!')
    r"\$?[A-Za-z]{1,3}\$?[0-9]{1,6}"
    r"(?:\:\$?[A-Za-z]{1,3}\$?[0-9]{1,6})?"
)

########################################################################
# 2) Updated token specification: add ERROR and STRING tokens, include '^' and '&'
########################################################################
token_spec = [
    ("ERROR", r"#(REF!|VALUE!|NAME\?|N/A|DIV/0!|NUM!|NULL!)"),
    ("REF", REF_PATTERN),
    ("BOOL", r"[Tt][Rr][Uu][Ee]|[Ff][Aa][Ll][Ss][Ee]"),
    ("STRING", r'"[^"]*"'),
    ("NUM",  r"[0-9]+(\.[0-9]+)?"),
    ("FUNC", r"[A-Za-z_]+"),
    # Match multi-character operators first.
    ("OP",   r"<=|>=|<>|[+\-*/=<>%^&]"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("COMMA",  r","),
    ("WS",     r"\s+"),
]

token_regex = "|".join(f"(?P<{name}>{pattern})" for (name, pattern) in token_spec)
tokenizer = re.compile(token_regex)

def arrayify(val, scalar_func=lambda x: x):
    if isinstance(val, list):
        return [arrayify(x, scalar_func) for x in val]
    else:
        return scalar_func(val)

def array_binop(a, b, op, op_label=None):
    # If an operand is an XlArray, convert it to a list-of-lists using its .data attribute.
    from .xltypes import XlArray  # adjust the import path if needed
    if isinstance(a, XlArray):
        a = a.data.tolist()
    if isinstance(b, XlArray):
        b = b.data.tolist()

    # Now treat both operands as lists (or scalars)
    if not isinstance(a, list) and not isinstance(b, list):
        intermediate = op(a, b)
##        if op_label:
##            print(f"DEBUG => array_binop => performing {a} {op_label} {b}, result={intermediate}")
##        else:
##            print(f"DEBUG => array_binop => performing op({a}, {b}), result={intermediate}")
        return intermediate
    elif isinstance(a, list) and not isinstance(b, list):
        #print(f"DEBUG => array_binop list-scalar: a={a}, b={b}")
        return [array_binop(x, b, op, op_label) for x in a]
    elif not isinstance(a, list) and isinstance(b, list):
        #print(f"DEBUG => array_binop scalar-list: a={a}, b={b}")
        return [array_binop(a, x, op, op_label) for x in b]
    else:
        #print(f"DEBUG => array_binop list-list: a={a}, b={b}")
        out = []
        for x, y in zip(a, b):
            out.append(array_binop(x, y, op, op_label))
        return out

def propagate_numeric_op(x, y, op):
    """
    Try to convert x and y to floats and then apply the operator 'op'.
    If either conversion fails or if x or y is an error value,
    return that error (or nonnumeric value) to propagate the error.
    """
    from .funcs.xlerrors import ValueExcelError  # adjust import as needed

    # -- Fix: treat None as zero in numeric contexts --
    if x is None:
        x = 0
    if y is None:
        y = 0
    # -----------------------------------------------
    
    if isinstance(x, ValueExcelError):
         return x
    if isinstance(y, ValueExcelError):
         return y
    try:
        x_val = float(x)
    except (ValueError, TypeError):
        return x  # propagate the error value (or nonnumeric)
    try:
        y_val = float(y)
    except (ValueError, TypeError):
        return y  # propagate the error value (or nonnumeric)
    return op(x_val, y_val)

def op_add(a, b):
    return array_binop(a, b, lambda x, y: propagate_numeric_op(x, y, lambda x, y: x + y))

def op_sub(a, b):
    #print(f"DEBUG => REALLY in my local op_sub, a={a}, b={b}")
    # Check if both operands appear to be arrays
    if hasattr(a, 'flat') and hasattr(b, 'flat') and hasattr(a, 'shape'):
        # Perform element-by-element subtraction using the flat lists.
        result_flat = [x - y for x, y in zip(a.flat, b.flat)]
        nrows, ncols = a.shape
        # Reconstruct a list-of-lists if needed (for multi-row arrays)
        if nrows > 1:
            result = []
            for i in range(nrows):
                start = i * ncols
                result.append(result_flat[start:start + ncols])
        else:
            # For a single row, just use the flat list
            result = result_flat
        # Return a new XlArray with the resulting data.
        return XlArray(result)
    else:
        # Fallback for scalar or list operations.
        result = array_binop(a, b, lambda x, y: propagate_numeric_op(x, y, lambda x, y: x - y))
        #print(f"DEBUG => op_sub => result={result}")
        return result

def op_mul(a, b):
    return array_binop(a, b, lambda x, y: propagate_numeric_op(x, y, lambda x, y: x * y))

def op_div(a, b):
    return array_binop(a, b, lambda x, y: propagate_numeric_op(x, y, lambda x, y: 0 if y == 0 else x / y))

def op_eq(a, b):
    # For equality comparisons we don’t force a numeric conversion.
    return array_binop(a, b, lambda x, y: 1 if x == y else 0)

def op_gt(a, b):
    return array_binop(a, b, lambda x, y: propagate_numeric_op(x, y, lambda x, y: 1 if x > y else 0))

def op_lt(a, b):
    return array_binop(a, b, lambda x, y: propagate_numeric_op(x, y, lambda x, y: 1 if x < y else 0))

def op_le(a, b):
    return array_binop(a, b, lambda x, y: propagate_numeric_op(x, y, lambda x, y: 1 if x <= y else 0))

def op_ge(a, b):
    return array_binop(a, b, lambda x, y: propagate_numeric_op(x, y, lambda x, y: 1 if x >= y else 0))

def op_ne(a, b):
    return array_binop(a, b, lambda x, y: propagate_numeric_op(x, y, lambda x, y: 1 if x != y else 0))

def op_pow(a, b):
    return array_binop(a, b, lambda x, y: propagate_numeric_op(x, y, lambda x, y: x ** y))

def op_concat(a, b):
    return array_binop(a, b, lambda x, y: str(x) + str(y))

# Mapping from operator symbols to functions
INFIX_OP_TO_FUNC = {
    '+': op_add,
    '-': op_sub,
    '*': op_mul,
    '/': op_div,
    '=': op_eq,
    '>': op_gt,
    '<': op_lt,
    '<=': op_le,
    '>=': op_ge,
    '<>': op_ne,
    '^': op_pow,
    '&': op_concat,
}

PREFIX_OP_TO_FUNC = {
    '-': lambda x: arrayify(x, lambda v: -v)
}

POSTFIX_OP_TO_FUNC = {
    '%': lambda x: arrayify(x, lambda v: v / 100),
}

class ASTNode:
    def __init__(self, token):
        self.token = token
        self.is_array_formula = False

    @property
    def tvalue(self):
        return self.token.tvalue

    @property
    def ttype(self):
        return self.token.ttype

    def eval(self, context):
        raise NotImplementedError()

class OperandNode(ASTNode):
    def eval(self, context):
        val = self.tvalue
        try:
            return float(val)
        except:
            return val

########################################################################
# RangeNode: splits on '!' to get sheet vs. cell reference.
########################################################################
class RangeNode(ASTNode):
    """Node for references like A1, B2, or 'Sheet'!A1:B2."""
    def eval(self, context):
        rng_str = self.tvalue
        if '!' in rng_str:
            sheet_part, rng_part = rng_str.split('!', 1)
            sheet_name = sheet_part.strip().strip("'")
        else:
            sheet_name = context.sheet
            rng_part   = rng_str

        # Add debug info before resolving
        #print(f"DEBUG: RangeNode.eval: rng_str={rng_str}, sheet_name={sheet_name}, rng_part={rng_part}")

        if ':' in rng_part:
            addrs = context.model.resolve_range(sheet_name, rng_part)
            # Debug: print out the resolved addresses
            #print(f"DEBUG: RangeNode.eval: Resolved addresses for {rng_part} -> {addrs}")
            return group_addresses_and_fetch(context, addrs)
        else:
            # For a single cell reference, instead of evaluating its value immediately,
            # return a reference wrapper that preserves the underlying CellAddress.
            addr_obj = CellAddress.from_string(rng_part)
            if not addr_obj.sheet:
                addr_obj.sheet = sheet_name
            return XlReference(addr_obj)

def group_addresses_and_fetch(context, addr_objs):
    if not addr_objs:
        return []
    # Debug: print the entire list of addresses
    #print("DEBUG: group_addresses_and_fetch: addr_objs =", addr_objs)
    
    out = []
    current_row = addr_objs[0].row
    rowvals = []
    for addr in addr_objs:
##        print(f"DEBUG => group_addresses_and_fetch with {addr}")
##        print("group_addresses_and_fetch: Processing cell", addr)
        if addr.row != current_row:
            out.append(rowvals)
            rowvals = []
            current_row = addr.row
        cell = context.model.get_cell(addr)
        #print(f"DEBUG: get_cell: Found cell {cell} for {addr}")
        val = context.eval_cell_value(cell)
        #print("group_addresses_and_fetch: Evaluated cell", addr, "to", val)
        # Dereference any XlReference so that we get the actual numeric value.
        while isinstance(val, XlReference):
            new_val = val.get_value(context)
            if new_val == val:
                break
            val = new_val
        rowvals.append(val)
    if rowvals:
        out.append(rowvals)
    result = out[0] if len(out) == 1 else out
    return XlArray(result)

class OperatorNode(ASTNode):
    def __init__(self, token, left=None, right=None):
        super().__init__(token)
        self.left = left
        self.right = right
        #print(f"DEBUG => OperatorNode.__init__: {token.tvalue}, left={left}, right={right}")

    def is_single_cell_reference(self, xlref):
        """
        Returns True if the XlReference represents a single cell.
        Assumes that xlref.get_address() returns a string such as "$A$1" for a single cell,
        and a range string like "$A$1:$B$2" if it is multi-cell.
        """
        addr = xlref.get_address()
        return ':' not in str(addr)

    def eval(self, context):
        if self.ttype == "OP_PREFIX":
            f = PREFIX_OP_TO_FUNC.get(self.tvalue)
            val = self.right.eval(context)
            if isinstance(val, XlReference):
                if self.is_single_cell_reference(val):
                    cell = context.model.get_cell(val.get_address())
                    val = context.eval_cell_value(cell)
                else:
                    # For multi-cell references, obtain the full array.
                    val = val.get_value(context)
            return f(val) if f else 0

        elif self.ttype == "OP_POSTFIX":
            f = POSTFIX_OP_TO_FUNC.get(self.tvalue)
            val = self.left.eval(context)
            if isinstance(val, XlReference):
                if self.is_single_cell_reference(val):
                    cell = context.model.get_cell(val.get_address())
                    val = context.eval_cell_value(cell)
                else:
                    val = val.get_value(context)
            return f(val) if f else 0

        elif self.ttype == "OP_INFIX":
            # Look up the function for this operator.
            f = INFIX_OP_TO_FUNC.get(self.tvalue)

            # Evaluate the left and right children.
            raw_lv = self.left.eval(context)
            raw_rv = self.right.eval(context)

            # Helper to resolve an operand:
            # - If the operand is an XlReference, then return its dereferenced value.
            # - If the operand is a list or numpy array (but not already an XlArray), then wrap it.
            # - Otherwise, return it unchanged.
            import numpy as np
            from .xltypes import XlArray
            def resolve_operand(val):
                if isinstance(val, XlReference):
                    if self.is_single_cell_reference(val):
                        cell = context.model.get_cell(val.get_address())
                        return context.eval_cell_value(cell)
                    else:
                        return val.get_value(context)
                elif isinstance(val, (list, np.ndarray)) and not isinstance(val, XlArray):
                    return XlArray(np.array(val))
                return val

            lv = resolve_operand(raw_lv)
            rv = resolve_operand(raw_rv)

            #print(f"DEBUG => OperatorNode '{self.tvalue}': left={lv}, right={rv}")
##            if self.tvalue == '-':
##                print("DEBUG => calling op_sub(lv, rv)")
            result = f(lv, rv) if f else 0
            # If the result is not scalar and not already an XlArray, then wrap it.
            if not np.isscalar(result) and not isinstance(result, XlArray):
                result = XlArray(result)
            return result

class FunctionNode(ASTNode):
    def __init__(self, token, args):
        super().__init__(token)
        self.args = args

    def eval(self, context):
        func_name = self.tvalue.upper()
        argvals = [a.eval(context) for a in self.args]
        #print(f"DEBUG => FunctionNode '{func_name}' with args={argvals}")
        result = context.call_function(func_name, argvals)
        #print(f"DEBUG => '{func_name}' returned {result}")
        return result

########################################################################
# FormulaParser: handles operator precedence using multiple levels.
########################################################################
class FormulaParser:
    """
    REFACTORED to handle operator precedence:
      expression      := comparison
      comparison      := concat ( ( "=" | "<" | ">" | "<=" | ">=" | "<>" ) concat )*
      concat          := addition ( '&' addition )*
      addition        := term ( ('+' | '-') term )*
      term            := exponentiation ( ('*' | '/') exponentiation )*
      exponentiation  := unary ( '^' exponentiation )?
      unary           := ('-' unary) | atom
      atom            := FUNC(...) | REF | STRING | NUM | ERROR | '(' expression ')'
    """
    def parse(self, formula):
        # Save the original object to use later in case we need an alternate attribute.
        orig_obj = formula
        #print(f"DEBUG: Initial formula type: {type(formula)}; value: {formula}")
    
        # Repeatedly unwrap the formula if it isn’t a string.
        seen = set()
        while not isinstance(formula, str):
            if id(formula) in seen:
                #print("DEBUG: Cycle detected; forcing conversion to string")
                logger.debug("Cycle detected; forcing conversion to string")
                formula = str(formula)
                break
            seen.add(id(formula))
            if hasattr(formula, "formula"):
                new_formula = formula.formula
                #print(f"DEBUG: Unwrapped via 'formula' attribute: {new_formula} (type: {type(new_formula)})")
                # Check for self-reference.
                if new_formula is formula:
                    if hasattr(formula, "_formula") and isinstance(formula._formula, str):
                        #print("DEBUG: 'formula' is self-referential; using '_formula' attribute instead.")
                        formula = formula._formula
                    else:
                        #print("DEBUG: 'formula' is self-referential and no alternate found; converting to string")
                        formula = str(formula)
                        break
                else:
                    formula = new_formula
            elif hasattr(formula, "value"):
                new_formula = formula.value
                #print(f"DEBUG: Unwrapped via 'value' attribute: {new_formula} (type: {type(new_formula)})")
                formula = new_formula
            else:
                #print("DEBUG: No unwrap attribute found; converting to string")
                formula = str(formula)
                break
    
        # Check if the resulting string still contains "ArrayFormula"
        if isinstance(formula, str) and "ArrayFormula" in formula:
            #print("DEBUG: Formula string appears to be the default ArrayFormula repr; attempting alternative extraction")
            try:
                # Try to get an alternative formula string from the original object.
                candidate = getattr(orig_obj, "_formula", None)
                if candidate and isinstance(candidate, str):
                    formula = candidate
##                    print("DEBUG: Extracted actual formula via '_formula' attribute")
##                else:
##                    print("DEBUG: '_formula' attribute not available or not a string")
            except Exception as e:
                #print("DEBUG: Exception when extracting '_formula':", e)
                logger.debug(f"Exception when extracting '_formula': {e}")
    
        #print(f"DEBUG: Final formula for tokenization: {formula}")
    
        # At this point, formula should be a proper string.
        form = formula.strip()
        self.is_array_formula = False
    
        # Handle array formulas enclosed in { ... }
        if form.startswith("{") and form.endswith("}"):
            self.is_array_formula = True
            if form.startswith("{="):
                form = form[2:-1].strip()
            else:
                form = form[1:-1].strip()
    
        # Remove leading '=' if present.
        if form.startswith("="):
            form = form[1:].strip()
    
        self.tokens = self._tokenize(form)
        self.index = 0
    
        root = self.parse_expression()
        root.is_array_formula = self.is_array_formula
        return root

    def _tokenize(self, formula_str):
        pos = 0
        tokens = []
        while pos < len(formula_str):
            m = tokenizer.match(formula_str, pos)
            if not m:
                raise ValueError(f"Invalid formula near: {formula_str[pos:]}")
            ttype = m.lastgroup
            tval = m.group(ttype)
            if ttype != "WS":
                new_token = Token(ttype, tval)
                #print(f"DEBUG tokenize => {new_token}")
                tokens.append(new_token)
            pos = m.end()
        return tokens

    def current_token(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None

    def consume(self, ttype=None):
        tk = self.current_token()
        if tk is None:
            raise ValueError(f"Expected {ttype}, but reached end of tokens")
        if ttype and tk.ttype != ttype:
            raise ValueError(f"Expected {ttype}, got {tk.ttype} (value: {tk.tvalue}) at token index {self.index}")
        self.index += 1
        return tk

    # expression := comparison
    def parse_expression(self):
        return self.parse_comparison()

    # comparison := concat (( "=" | "<" | ">" | "<=" | ">=" | "<>" ) concat)*
    def parse_comparison(self):
        left = self.parse_concat()
        while True:
            tk = self.current_token()
            if tk and tk.ttype == "OP" and tk.tvalue in ('=', '<', '>', '<=', '>=', '<>'):
                op_tok = self.consume("OP")
                node = OperatorNode(op_tok, left=left)
                node.token.ttype = "OP_INFIX"
                right = self.parse_concat()
                node.right = right
                left = node
            else:
                break
        return left

    # concat := addition ( '&' addition )*
    def parse_concat(self):
        left = self.parse_addition()
        while True:
            tk = self.current_token()
            if tk and tk.ttype == "OP" and tk.tvalue == '&':
                op_tok = self.consume("OP")
                node = OperatorNode(op_tok, left=left)
                node.token.ttype = "OP_INFIX"
                right = self.parse_addition()
                node.right = right
                left = node
            else:
                break
        return left

    # addition := term ( ('+' | '-') term )*
    def parse_addition(self):
        left = self.parse_term()
        while True:
            tk = self.current_token()
            if tk and tk.ttype == "OP" and tk.tvalue in ('+', '-'):
                op_tok = self.consume("OP")
                node = OperatorNode(op_tok, left=left)
                node.token.ttype = "OP_INFIX"
                right = self.parse_term()
                node.right = right
                left = node
            else:
                break
        return left

    # term := exponentiation ( ('*' | '/') exponentiation )*
    def parse_term(self):
        left = self.parse_exponentiation()
        while True:
            tk = self.current_token()
            if tk and tk.ttype == "OP" and tk.tvalue in ('*', '/'):
                op_tok = self.consume("OP")
                node = OperatorNode(op_tok, left=left)
                node.token.ttype = "OP_INFIX"
                right = self.parse_exponentiation()
                node.right = right
                left = node
            else:
                break
        return left

    # exponentiation := unary ( '^' exponentiation )?
    def parse_exponentiation(self):
        left = self.parse_unary()
        tk = self.current_token()
        if tk and tk.ttype == "OP" and tk.tvalue == '^':
            op_tok = self.consume("OP")
            node = OperatorNode(op_tok, left=left)
            node.token.ttype = "OP_INFIX"
            node.right = self.parse_exponentiation()
            return node
        return left

    # unary := ('-' unary) | atom
    def parse_unary(self):
        tk = self.current_token()
        if tk and tk.ttype == "OP" and tk.tvalue == '-':
            op_tok = self.consume("OP")
            node = OperatorNode(op_tok)
            node.token.ttype = "OP_PREFIX"
            node.right = self.parse_unary()
            return node
        return self.parse_atom()

    # atom := FUNC(...) | REF | STRING | NUM | ERROR | '(' expression ')'
    def parse_atom(self):
        tk = self.current_token()
        if not tk:
            return OperandNode(Token("NUM", "0"))
        if tk.ttype == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr
        elif tk.ttype == "BOOL":
            self.consume("BOOL")
            bool_val = (tk.tvalue.upper() == "TRUE")
            return OperandNode(Token("NUM", "1" if bool_val else "0"))
        elif tk.ttype == "STRING":
            self.consume("STRING")
            literal = tk.tvalue[1:-1]  # Remove the surrounding quotes.
            return OperandNode(Token("STRING", literal))
        elif tk.ttype == "ERROR":
            err_tok = self.consume("ERROR")
            return OperandNode(err_tok)
        elif tk.ttype == "FUNC":
            func_tok = self.consume("FUNC")
            self.consume("LPAREN")
            args = []
            if self.current_token() and self.current_token().ttype != "RPAREN":
                args.append(self.parse_expression())
                while self.current_token() and self.current_token().ttype == "COMMA":
                    self.consume("COMMA")
                    args.append(self.parse_expression())
            self.consume("RPAREN")
            return FunctionNode(func_tok, args)
        elif tk.ttype == "REF":
            ref_tok = self.consume("REF")
            node = RangeNode(ref_tok)
            nxt = self.current_token()
            if nxt and nxt.ttype == "LPAREN":
                raise ValueError("Unexpected '(' after cell reference; did you forget an operator (e.g., '&')?")
            if nxt and nxt.ttype == "OP" and nxt.tvalue == '%':
                op_tok = self.consume("OP")
                opnode = OperatorNode(op_tok, left=node)
                opnode.token.ttype = "OP_POSTFIX"
                return opnode
            return node
        elif tk.ttype == "NUM":
            num_tok = self.consume("NUM")
            node = OperandNode(num_tok)
            nxt = self.current_token()
            if nxt and nxt.ttype == "OP" and nxt.tvalue == '%':
                op_tok = self.consume("OP")
                opnode = OperatorNode(op_tok, left=node)
                opnode.token.ttype = "OP_POSTFIX"
                return opnode
            return node
        else:
            self.consume()
            return OperandNode(Token("NUM", "0"))

    def create_node(self, token):
        if token.ttype == "operand":
            if token.tsubtype in ["range", "pointer"]:
                return RangeNode(token)
            else:
                return OperandNode(token)
        elif token.ttype == "FUNC":
            return FunctionNode(token, [])
        elif token.ttype.startswith("OP"):
            return OperatorNode(token)
        else:
            raise ValueError('Unknown token type: ' + token.ttype)

    def build_ast(self, nodes):
        stack = []
        for node in nodes:
            if isinstance(node, OperatorNode):
                if node.ttype == "OP_INFIX":
                    node.right = stack.pop()
                    node.left = stack.pop()
                else:
                    node.right = stack.pop()
            elif isinstance(node, FunctionNode):
                args = []
                for _ in range(node.num_args):
                    args.append(stack.pop())
                node.args = list(reversed(args))
            stack.append(node)
        return stack.pop()
