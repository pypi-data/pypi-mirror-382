##model.py

import json
import jsonpickle
import gzip
import os
import pickle

from .references import CellAddress, col_letters_to_num, col_num_to_letters
from .utils import parse_xl_range, MAX_COL, MAX_ROW
from .parser import FormulaParser

class Cell:
    def __init__(self, address_obj: CellAddress, value=None, formula=None, blank=False):
        self.address_obj = address_obj
        self.value = value
        self.formula = formula
        self.blank = blank
        self.need_update = False
        self.parsed_ast = None

    def __repr__(self):
        return (f"<Cell {self.address_obj.to_string()} "
                f"value={self.value!r} formula={self.formula!r} blank={self.blank}>")

    def to_dict(self):
        return {
            "address": self.address_obj.to_string(),
            "value": self.value,
            "formula": self.formula,
            "need_update": self.need_update,
            "blank": self.blank
        }

class Sheet:
    def __init__(self, name: str):
        self.name = name
        self.cells = {}  # local_key -> Cell

    def __repr__(self):
        return f"<Sheet {self.name!r} with {len(self.cells)} cells>"

    def set_cell(self, cell):
        local_key = f"{cell.address_obj.column.upper()}{cell.address_obj.row}"
        self.cells[local_key] = cell

    def get_cell(self, col: str, row: int):
        local_key = f"{col.upper()}{row}"
        return self.cells.get(local_key)

    def to_dict(self):
        return {
            "name": self.name,
            "cells": {k: c.to_dict() for (k, c) in self.cells.items()}
        }

class Model:
    def __init__(self):
        self.sheets = {}
        self.defined_names = {}
        # Keep the adjacency for dependencies in memory here
        self.dependency_graph = {}  # cell -> list of canonical addresses it depends on

        # Cache for upstream dependency sets to avoid recomputation
        self.upstream_cache = {}
        # Cache for resolved ranges to avoid repeated address generation
        self.range_cache = {}
        # Reverse dependency graph (dependents) built alongside dependency_graph
        self.reverse_dependency_graph = {}
        
    def create_sheet(self, name):
        if name not in self.sheets:
            self.sheets[name] = Sheet(name)
        return self.sheets[name]

##    def set_cell_value(self, address_obj: CellAddress, value=None, formula=None):
    def set_cell_value(self, address_obj: CellAddress, value=None, formula=None, blank=False):
        sheet_name = address_obj.sheet or "Sheet1"
        address_obj.sheet = sheet_name
        sh = self.create_sheet(sheet_name)
##        c = Cell(address_obj, value, formula)
        c = Cell(address_obj, value, formula, blank)
        sh.set_cell(c)

    def get_cell(self, address_obj: CellAddress):
        sheet_name = address_obj.sheet or "Sheet1"
        address_obj.sheet = sheet_name
        sh = self.sheets.get(sheet_name)
        if not sh:
            return None
        cell = sh.get_cell(address_obj.column, address_obj.row)
##        if cell is None:
##            print(f"DEBUG: get_cell: No cell found for {address_obj} on sheet '{sheet_name}'")
##        else:
##            print(f"DEBUG: get_cell: Found cell {cell} for {address_obj}")
        return cell

    def get_cell_by_canonical_address(self, canonical_addr: str):
        try:
            sheet_name, local_key = canonical_addr.split("!")
        except ValueError:
            sheet_name = "Sheet1"
            local_key = canonical_addr
##        # Normalize the local key using CellAddress.from_string to get the absolute reference
##        local_key = CellAddress.from_string(local_key).to_string(include_sheet=False)
        # Normalize the local key by stripping out '$'
        local_key = local_key.replace('$', '')
        sheet = self.sheets.get(sheet_name)
        if sheet is None:
            return None
        return sheet.cells.get(local_key)

    def to_dict(self):
        """
        Convert the model to a serializable dict, including sheets, defined names,
        and the stored dependency graph.
        """
        return {
            "sheets": {
                sname: sobj.to_dict()
                for (sname, sobj) in self.sheets.items()
            },
            "defined_names": {
                name: cell.to_string()
                for name, cell in self.defined_names.items()
            },
            # Include the dependency graph so it’s persisted in the JSON
            "dependency_graph": self.dependency_graph
        }

    def to_json(self) -> str:
        """Simple helper to return a pretty‐printed JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Rebuild a Model from the dict structure, restoring
        sheets/cells, defined names, and the dependency graph.
        """
        m = cls()
        # 1) Sheets & Cells
        for sheet_name, sheet_data in data.get("sheets", {}).items():
            sh = m.create_sheet(sheet_name)
            for local_key, cell_data in sheet_data["cells"].items():
                addr_str = cell_data["address"]
                addr_obj = CellAddress.from_string(addr_str)
                c = Cell(addr_obj,
                         cell_data.get("value"),
                         cell_data.get("formula"),
                         cell_data.get("blank", False))
                c.need_update = cell_data.get("need_update", True)
                sh.set_cell(c)
        # 2) Defined names
        defined_names = data.get("defined_names", {})
        for name, addr_str in defined_names.items():
            try:
                addr_obj = CellAddress.from_string(addr_str)
                if not addr_obj.sheet:
                    addr_obj.sheet = "Sheet1"
                m.defined_names[name] = addr_obj
            except Exception:
                pass
        # 3) Dependency Graph
        m.dependency_graph = data.get("dependency_graph", {})
        # Upstream cache will be computed lazily
        m.upstream_cache = {}
        # Build reverse dependency graph from the adjacency list
        from .dependency import build_reverse_dependency_graph
        m.reverse_dependency_graph = build_reverse_dependency_graph(m)
        return m

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    def resolve_range(self, sheet_name: str, rng_str: str):
        #print(f"DEBUG => resolve_range called with sheet_name={sheet_name}, rng_str={rng_str}")
        key = (sheet_name, rng_str)
        cache = getattr(self, "range_cache", None)
        if cache is not None and key in cache:
            return cache[key]
        
        if ':' not in rng_str:
            addr = CellAddress.from_string(rng_str)
            if not addr.sheet:
                addr.sheet = sheet_name
            result = [addr]
        else:
            min_col, min_row, max_col, max_row = parse_xl_range(rng_str)
            result = []
            for r in range(min_row, max_row + 1):
                for c in range(min_col, max_col + 1):
                    col_letters = col_num_to_letters(c)
                    addr_obj = CellAddress(sheet=sheet_name, column=col_letters, row=r)
                    result.append(addr_obj)

        if cache is not None:
            cache[key] = result
        return result

    def persist_to_json_file(self, fname):
        """
        Serialize (via jsonpickle) to disk, optionally .gz compressed.
        This includes the entire model (sheets, cells, dependency_graph).
        """
        serialized = jsonpickle.encode(self, keys=True)
        is_gz = os.path.splitext(fname)[-1].lower() in ('.gz', '.gzip')
        file_open = gzip.GzipFile if is_gz else open
        mode = 'wb' if is_gz else 'w'
        with file_open(fname, mode) as fp:
            if is_gz:
                fp.write(serialized.encode('utf-8'))
            else:
                fp.write(serialized)

    def persist_to_pickle_file(self, fname):
        """Persist using Python pickle for faster load times."""
        data = pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL)
        is_gz = os.path.splitext(fname)[-1].lower() in ('.gz', '.gzip')
        file_open = gzip.GzipFile if is_gz else open
        mode = 'wb'
        with file_open(fname, mode) as fp:
            fp.write(data)
            
    @classmethod
    def construct_from_json_file(cls, fname, build_code=False):
        """
        Load from a JSON or GZ file, optionally calling build_code afterward.
        """
        is_gz = os.path.splitext(fname)[-1].lower() in ('.gz', '.gzip')
        file_open = gzip.GzipFile if is_gz else open
        mode = 'rb' if is_gz else 'r'
        with file_open(fname, mode) as fp:
            if is_gz:
                data_bytes = fp.read()
                data_str = data_bytes.decode('utf-8')
            else:
                data_str = fp.read()

        obj = jsonpickle.decode(data_str, keys=True)
        # Ensure new cache attribute exists even if not persisted
        if not hasattr(obj, 'upstream_cache'):
            obj.upstream_cache = {}
        if not hasattr(obj, 'range_cache'):
            obj.range_cache = {}
        if not hasattr(obj, 'reverse_dependency_graph'):
            from .dependency import build_reverse_dependency_graph
            obj.reverse_dependency_graph = build_reverse_dependency_graph(obj)
            
        if build_code and hasattr(obj, 'build_code'):
            obj.build_code()
        return obj

    @classmethod
    def construct_from_pickle_file(cls, fname, build_code=False):
        """Load a model persisted with :func:`persist_to_pickle_file`."""
        is_gz = os.path.splitext(fname)[-1].lower() in ('.gz', '.gzip')
        file_open = gzip.GzipFile if is_gz else open
        mode = 'rb'
        with file_open(fname, mode) as fp:
            data = fp.read()
        obj = pickle.loads(data)
        if not hasattr(obj, 'upstream_cache'):
            obj.upstream_cache = {}
        if not hasattr(obj, 'range_cache'):
            obj.range_cache = {}
        if not hasattr(obj, 'reverse_dependency_graph'):
            from .dependency import build_reverse_dependency_graph
            obj.reverse_dependency_graph = build_reverse_dependency_graph(obj)
        if build_code and hasattr(obj, 'build_code'):
            obj.build_code()
        return obj
    
    def build_code(self):
        """
        Parse formulas into AST, then build the dependency graph.
        """
        parser = FormulaParser()
        from .compiler import compile_cell
        for sheet_name, sheet_obj in self.sheets.items():
            for local_key, cell_obj in sheet_obj.cells.items():
                if cell_obj.formula:
                    ast_result = parser.parse(cell_obj.formula)
                    cell_obj.parsed_ast = ast_result
                    compile_cell(cell_obj, self)

        # Build the dependency graph right after parsing:
        self.build_dependency_graph()

    def build_dependency_graph(self):
        """
        Build an adjacency list: cell -> list of cells it depends on.
        We'll store it in self.dependency_graph, keyed by canonical address.
        """
        from .dependency import extract_references_from_ast

        self.dependency_graph.clear()
        # Any cached upstream sets are now invalid
        self.upstream_cache.clear()
        self.reverse_dependency_graph = {}
        
        for sheet_name, sheet_obj in self.sheets.items():
            for local_key, cell_obj in sheet_obj.cells.items():
                if cell_obj.formula and cell_obj.parsed_ast:
                    this_canonical = f"{sheet_name}!{local_key}"
                    refs = extract_references_from_ast(cell_obj.parsed_ast, self, sheet_name)
                    self.dependency_graph[this_canonical] = list(refs)
                else:
                    # For non-formula cells, store an empty list or skip
                    pass

        # Build reverse dependency graph for dependents lookup
        from .dependency import build_reverse_dependency_graph
        self.reverse_dependency_graph = build_reverse_dependency_graph(self)
        
    def set_defined_name(self, name: str, addr_str: str):
        try:
            addr_obj = CellAddress.from_string(addr_str)
            if not addr_obj.sheet:
                addr_obj.sheet = "Sheet1"
            self.defined_names[name] = addr_obj
        except Exception as e:
            raise ValueError(f"Invalid address for defined name {name}: {addr_str}") from e

    def resolve_defined_name(self, name: str, current_sheet: str) -> CellAddress:
        """
        First check the defined_names dictionary. If not found, search the current sheet,
        and if still not found, search all sheets.
        """
        if name in self.defined_names:
            return self.defined_names[name]

        # Try current sheet first
        if current_sheet in self.sheets:
            sheet = self.sheets[current_sheet]
            for cell in sheet.cells.values():
                if (isinstance(cell.value, str) and
                    cell.value.strip().lower() == name.strip().lower()):
                    return cell.address_obj

        # Search in all sheets
        for sheet in self.sheets.values():
            for cell in sheet.cells.values():
                if (isinstance(cell.value, str) and
                    cell.value.strip().lower() == name.strip().lower()):
                    return cell.address_obj

        raise KeyError(f"Defined name '{name}' not found on sheet '{current_sheet}' or any sheet.")
