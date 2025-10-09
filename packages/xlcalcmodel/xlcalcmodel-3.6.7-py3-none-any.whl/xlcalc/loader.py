# loader.py

import xlwings as xw
from .model import Model
from .references import CellAddress, col_letters_to_num, col_num_to_letters
import sys
sys.stdout.reconfigure(encoding='utf-8')

def load_workbook_to_model(filepath):
    """
    Read an .xlsx file using xlwings, build and return a Model.
    Excel (via COM) is used to extract the actual cell values and formulas.
    Once the model is built (e.g. as JSON), Excel is no longer needed.
    """
    # Launch Excel invisibly.
    app = xw.App(visible=False)
    try:
        wb = xw.Book(filepath)
    except Exception as e:
        app.quit()
        raise e

    model = Model()

    # Loop through each sheet in the workbook.
    for sht in wb.sheets:
        print(f"DEBUG: Processing sheet: {sht.name}")
        # First, get the used_range:
        used_rng = sht.used_range
        # Determine its boundaries
        try:
            start_addr, end_addr = used_rng.address.split(":")
        except Exception:
            # If used_range returns a single cell, duplicate it.
            start_addr = used_rng.address
            end_addr = used_rng.address

        start_cell = CellAddress.from_string(start_addr)
        end_cell = CellAddress.from_string(end_addr)
        # Add extra margin so that any cells referenced outside the used range are captured.
        extra_rows = 2
        extra_cols = 2
        max_row = end_cell.row + extra_rows
        max_col = col_letters_to_num(end_cell.column) + extra_cols

        # Build a full range string covering from A1 to the expanded max cell.
        full_range_str = "A1:" + col_num_to_letters(max_col) + str(max_row)
        full_range = sht.range(full_range_str)
        
        # Iterate over all cells in the full_range.
        for row in full_range.rows:
            for cell in row:
                cell_addr_str = cell.address
                try:
                    addr = CellAddress.from_string(cell_addr_str)
                except Exception as e:
                    print(f"DEBUG: Error parsing address {cell_addr_str}: {e}")
                    continue
                addr.sheet = sht.name

                # Extract the cell's value and formula.
                cell_value = cell.value
                cell_formula = cell.formula  # xlwings returns the formula as entered.
                
                # Determine if this is simply a constant.
                if cell_formula is None or cell_formula == "":
                    cell_formula = None
                else:
                    # Remove the leading "=" (if present) and any whitespace.
                    formula_body = cell_formula.lstrip("=").strip()
                    if cell_value is not None and isinstance(cell_value, (int, float)):
                        numeric_str = str(cell_value)
                        int_str = str(int(cell_value)) if (isinstance(cell_value, float) and cell_value == int(cell_value)) else numeric_str
                        if formula_body == numeric_str or formula_body == int_str:
                            cell_formula = None  # It’s just a constant.
                    else:
                        if str(cell_value).strip() == formula_body:
                            cell_formula = None
                        else:
                            if not cell_formula.startswith("="):
                                cell_formula = "=" + cell_formula

                #THESE ARE NEEDED TO SEED THE ITERATIVE CALCULATIONS - So commenting this out.
                #if cell_formula is not None:
                #    cell_value = None

                #Add a cell if it has a value or a formula AND include BLANK cells for model/dependency map completeness.
                blank_cell = cell_value is None and cell_formula is None
                print(f"DEBUG: Setting cell {addr} with value: {cell_value}, formula: {cell_formula}")
                model.set_cell_value(
                    address_obj=addr,
                    value=cell_value,
                    formula=cell_formula,
                    blank=blank_cell
                )
        print(f"DEBUG: Finished processing sheet: {sht.name}")

    # Close the workbook and quit Excel.
    wb.close()
    app.quit()

    return model
