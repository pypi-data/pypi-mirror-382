# financial_funcs.py
"""
Excel-like financial functions adapted from xlcalculator:
  IRR, NPV, PMT, PV, SLN, VDB, XIRR, XNPV.

Requires:
 - numpy_financial (npf)
 - pandas (for XIRR, XNPV, internal DataFrame usage)
 - scipy (for newton method in XIRR if not convergent)
"""

import numpy_financial as npf
import pandas as pd
from math import isclose
from scipy.optimize import newton
from typing import Tuple

from . import xl, xlerrors, func_xltypes

########################################
# IRR, NPV
########################################

@xl.register()
@xl.validate_args
def IRR(
    values: func_xltypes.XlArray,
    guess: func_xltypes.XlNumber = None
) -> func_xltypes.XlNumber:
    """
    Returns the internal rate of return for a series of cash flows.
    https://support.microsoft.com/en-us/office/irr-function-64925eaa-9988-495b-b290-3ad0c163c1bc
    """
    cashflows = [float(v) for v in values.flat]
    try:
        return npf.irr(cashflows)
    except Exception as e:
        raise xlerrors.NumExcelError(f"IRR error: {e}")


@xl.register()
@xl.validate_args
def NPV(
        rate: func_xltypes.XlNumber,
        *values: Tuple[func_xltypes.XlNumber],
) -> func_xltypes.XlNumber:
    """Calculates the net present value of an investment by using a discount
    rate and a series of future payments (negative values) and income
    (positive values).

    https://support.office.com/en-us/article/
        npv-function-8672cb67-2576-4d07-b67b-ac28acf2a568
    """
    if not len(values):
        raise xlerrors.ValueExcelError('value1 is required')

    cashflow = [float(value) for value in values]
    rate = float(rate)

    if xl.COMPATIBILITY == 'PYTHON':
        return npf.npv(rate, cashflow)

    return sum([
        val * (1 + rate) ** - (i + 1)
        for (i, val) in enumerate(cashflow)
    ])


########################################
# PMT, PV
########################################

@xl.register()
@xl.validate_args
def PMT(
    rate: func_xltypes.XlNumber,
    nper: func_xltypes.XlNumber,
    pv: func_xltypes.XlNumber,
    fv: func_xltypes.XlNumber = 0,
    when: func_xltypes.XlNumber = 0
) -> func_xltypes.XlNumber:
    """
    Calculates the payment for a loan based on constant payments and
    a constant interest rate.
    https://support.microsoft.com/en-us/office/pmt-function-0214da64-9a63-4996-bc20-214433fa6441
    """
    rate_f = float(rate)
    nper_f = float(nper)
    pv_f = float(pv)
    fv_f = float(fv)
    when_f = int(when)

    try:
        return float(npf.pmt(rate_f, nper_f, pv_f, fv_f, when=when_f))
    except Exception as e:
        raise xlerrors.NumExcelError(f"PMT error: {e}")


@xl.register()
@xl.validate_args
def PV(
    rate: func_xltypes.XlNumber,
    nper: func_xltypes.XlNumber,
    pmt: func_xltypes.XlNumber,
    fv: func_xltypes.XlNumber = 0,
    when: func_xltypes.XlNumber = 0
) -> func_xltypes.XlNumber:
    """
    Calculates the present value of a loan or an investment, 
    based on a constant interest rate.
    https://support.microsoft.com/en-us/office/pv-function-23879d31-0e02-4321-be01-da16e8168cbd
    """
    rate_f = float(rate)
    nper_f = float(nper)
    pmt_f = float(pmt)
    fv_f = float(fv)
    when_f = int(when)

    try:
        return float(npf.pv(rate_f, nper_f, pmt_f, fv_f, when=when_f))
    except Exception as e:
        raise xlerrors.NumExcelError(f"PV error: {e}")


########################################
# SLN & VDB
########################################


@xl.register()
@xl.validate_args
def SLN(
    cost: func_xltypes.XlNumber,
    salvage: func_xltypes.XlNumber,
    life: func_xltypes.XlNumber
) -> func_xltypes.XlNumber:
    """
    Returns the straight-line depreciation of an asset for one period.
    https://support.microsoft.com/en-us/office/sln-function-cdb666e5-c1c6-40a7-806a-e695edc2f1c8
    """
    cost_f = float(cost)
    salvage_f = float(salvage)
    life_f = float(life)

    return (cost_f - salvage_f) / life_f


@xl.register()
@xl.validate_args
def VDB(
    cost: func_xltypes.XlNumber,
    salvage: func_xltypes.XlNumber,
    life: func_xltypes.XlNumber,
    start_period: func_xltypes.XlNumber,
    end_period: func_xltypes.XlNumber,
    factor: func_xltypes.XlNumber = 2,
    no_switch: func_xltypes.XlBoolean = False
) -> func_xltypes.XlNumber:
    """
    Returns the depreciation of an asset for any period specified 
    with Double Declining Balance by default. 
    This approach tries to match Excel's partial-year logic more closely.
    https://support.microsoft.com/en-us/office/vdb-function-dde4e207-f3fa-488d-91d2-66d55e861d73
    """
    # Convert
    cost_f = float(cost)
    salvage_f = float(salvage)
    life_f = float(life)
    sp = float(start_period)
    ep = float(end_period)
    factor_f = float(factor)
    no_switch_b = bool(no_switch)

    if cost_f <= 0 or life_f <= 0 or ep <= sp or salvage_f < 0:
        # A simple check if invalid => #NUM!
        raise xlerrors.NumExcelError("VDB: invalid arguments")

    # We'll do partial-year logic:
    # Reference: 
    # https://support.microsoft.com/en-us/office/vdb-function-dde4e207-f3fa-488d-91d2-66d55e861d73

    # We'll slice each period (month or fraction) from sp..ep in small steps
    # to closely match Excel's approach. 
    # Then apply DDB or SL each fraction. 
    # For large life, this is somewhat brute force but works well.

    # We'll accumulate total depreciation from sp to ep.
    remaining = cost_f
    total_dep = 0.0
    period = 0
    # track if we've switched to SL
    switched = no_switch_b

    # for each integer period in [0..life_f)
    while period < life_f:
        # for each fraction up to the next integer or ep
        # if we've fully reached ep, break
        current_start = max(sp, period)
        current_end = min(ep, period + 1)

        if current_start >= current_end:
            # no more intervals
            break

        # fraction for this sub-interval
        fraction = current_end - current_start
        if fraction < 0:
            break

        # compute the DDB for a full period => rate = factor / life_f
        ddb_for_full_period = remaining * (factor_f / life_f)
        # for fraction
        ddb_depr = ddb_for_full_period * fraction

        # compute what SL would be for that full period
        # if we haven't switched yet
        if not switched:
            # the remaining lifetime is (life_f - period)
            # a single full period of SL => (remaining - salvage_f) / (life_f - period)
            # * fraction
            if (life_f - period) < 1e-12:
                sl_for_full_period = 0
            else:
                sl_for_full_period = (remaining - salvage_f) / (life_f - period)
            sl_depr = sl_for_full_period * fraction

            # if DDB < SL => we switch
            if ddb_depr < sl_depr:
                switched = True
                # recalc with SL
                depr = sl_depr
            else:
                depr = ddb_depr
        else:
            # we already switched or no_switch => straight line
            if (life_f - period) < 1e-12:
                depr = 0
            else:
                depr = ((remaining - salvage_f) / (life_f - period)) * fraction

        # clamp so as not to go below salvage
        if depr > (remaining - salvage_f):
            depr = (remaining - salvage_f)

        total_dep += depr
        remaining -= depr

        if abs(remaining - salvage_f) < 1e-8:
            # we've hit salvage, no more depreciation
            break

        # done sub-interval
        # next period 
        if current_end >= ep:
            break

        # if the sub-interval ended exactly at period+1 => new period
        if abs(current_end - (period+1)) < 1e-12:
            period += 1
        else:
            # partial end => break
            break

    return total_dep


########################################
# XIRR & XNPV
########################################

def _xnpv(rate, values, dates):
    """
    Sums [value / (1+rate)^((date - first_date)/365)]
    """
    if rate <= -1.0:
        return float('inf')
    first_date = dates[0]
    total = 0.0
    for val, d in zip(values, dates):
        day_frac = (d - first_date) / 365.0
        total += val / ((1.0 + rate)**(day_frac))
    return total

def _xirr(values, dates, guess=0.1):
    """
    Solve xNPV=0 via Newton's method, more or less Excel approach.
    """
    def f(r):
        return _xnpv(r, values, dates)

    try:
        sol = newton(lambda r: f(r), guess, maxiter=100)
        # check closeness
        if not isclose(f(sol), 0.0, abs_tol=1e-7):
            raise xlerrors.NumExcelError("XIRR did not converge well")
        return sol
    except (RuntimeError, FloatingPointError):
        raise xlerrors.NumExcelError("XIRR did not converge")

@xl.register()
@xl.validate_args
def XIRR(
    values: func_xltypes.XlArray,
    dates: func_xltypes.XlArray,
    guess: func_xltypes.XlNumber = 0.1
) -> func_xltypes.XlNumber:
    """
    Returns the IRR for a schedule of cash flows that is not necessarily periodic.
    https://support.microsoft.com/en-us/office/xirr-function-de1242ec-6477-445b-b11b-a303ad9adc9d
    """
    cflows = [float(v) for v in values.flat]
    dts = [float(d) for d in dates.flat]

    if len(cflows) != len(dts):
        raise xlerrors.NumExcelError("XIRR => mismatch lengths")

    df = pd.DataFrame({"d": dts, "v": cflows})
    df = df[df["v"] != 0.0]
    df = df.sort_values("d", ascending=True)
    if df.empty:
        raise xlerrors.NumExcelError("XIRR => no non-zero flows")

    cvals = list(df["v"])
    cdates = list(df["d"])
    try:
        return float(_xirr(cvals, cdates, float(guess)))
    except Exception as e:
        raise xlerrors.NumExcelError(f"XIRR => {e}")


@xl.register()
@xl.validate_args
def XNPV(
    rate: func_xltypes.XlNumber,
    values: func_xltypes.XlArray,
    dates: func_xltypes.XlArray,
) -> func_xltypes.XlNumber:
    """
    Returns the net present value for a schedule of cash flows with irregular intervals.
    https://support.microsoft.com/en-us/office/xnpv-function-1b42bbf6-370f-4532-a0eb-d67c16b664b7
    """
    cflows = [float(v) for v in values.flat]
    dts = [float(d) for d in dates.flat]

    if len(cflows) != len(dts):
        raise xlerrors.NumExcelError("XNPV => mismatch lengths")

    return _xnpv(float(rate), cflows, dts)
