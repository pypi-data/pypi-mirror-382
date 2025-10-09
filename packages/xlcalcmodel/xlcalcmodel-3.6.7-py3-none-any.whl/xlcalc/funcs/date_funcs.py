# date_funcs.py

import datetime
import yearfrac
from dateutil.relativedelta import relativedelta
from dateutil import rrule

# Adjust these imports to match your package structure
from . import xl, xlerrors, func_xltypes
from . import date_utils  # This file provides EXCEL_EPOCH, number_to_datetime, datetime_to_number

def _now():
    """Hook for current date/time, so we can override in tests if needed."""
    return datetime.datetime.now()

@xl.register()
@xl.validate_args
def DATE(
    year: func_xltypes.XlNumber,
    month: func_xltypes.XlNumber,
    day: func_xltypes.XlNumber
) -> func_xltypes.XlNumber:
    """
    Returns an Excel serial number representing the given year/month/day.

    In Excel, DATE returns a float representing the date (with 1900-based system).
    """
    y = float(year)
    if not (0 < y < 9999):
        raise xlerrors.NumExcelError(f"Year must be between 1 and 9999, got {year}")

    # If your code wants to treat year < 1900 as an offset, do so:
    if y < 1900:
        y = 1900 + y

    # Build a Python datetime relative to 1900-01-01 (or your chosen epoch)
    delta = relativedelta(
        years=int(y - 1900),
        months=int(month) - 1,
        days=int(day) - 1
    )
    result_dt = date_utils.EXCEL_EPOCH + delta

    if result_dt <= date_utils.EXCEL_EPOCH:
        raise xlerrors.NumExcelError(f"Date result before {date_utils.EXCEL_EPOCH}")

    return date_utils.datetime_to_number(result_dt)


@xl.register()
@xl.validate_args
def DATEDIF(
    start_date: func_xltypes.XlNumber,
    end_date: func_xltypes.XlNumber,
    unit: func_xltypes.XlText
) -> func_xltypes.XlNumber:
    """
    Calculates the difference between two dates (in days/months/years).
    Returns a float count (e.g. 30.0 days).
    """
    if start_date > end_date:
        raise xlerrors.NumExcelError(
            f"Start date must be <= end date. Got Start: {start_date}, End: {end_date}"
        )

    dt_start = date_utils.number_to_datetime(float(start_date))
    dt_end   = date_utils.number_to_datetime(float(end_date))
    u = str(unit).upper()

    if u == "Y":
        date_list = list(rrule.rrule(rrule.YEARLY, dtstart=dt_start, until=dt_end))
        return float(len(date_list) - 1)
    elif u == "M":
        date_list = list(rrule.rrule(rrule.MONTHLY, dtstart=dt_start, until=dt_end))
        return float(len(date_list) - 1)
    elif u == "D":
        date_list = list(rrule.rrule(rrule.DAILY, dtstart=dt_start, until=dt_end))
        return float(len(date_list) - 1)
    elif u == "MD":
        # Compare day-of-month difference ignoring years/months
        mod_start = dt_start.replace(year=1900, month=1)
        mod_end   = dt_end.replace(year=1900, month=1)
        date_list = list(rrule.rrule(rrule.DAILY, dtstart=mod_start, until=mod_end))
        return float(len(date_list) - 1)
    elif u == "YM":
        # Compare month difference ignoring years/days
        mod_start = dt_start.replace(year=1900, day=1)
        mod_end   = dt_end.replace(year=1900, day=1)
        date_list = list(rrule.rrule(rrule.MONTHLY, dtstart=mod_start, until=mod_end))
        return float(len(date_list) - 1)
    elif u == "YD":
        # Compare day difference ignoring years
        mod_start = dt_start.replace(year=1900)
        mod_end   = dt_end.replace(year=1900)
        date_list = list(rrule.rrule(rrule.DAILY, dtstart=mod_start, until=mod_end))
        return float(len(date_list) - 1)
    else:
        raise xlerrors.NumExcelError(f"Invalid DATEDIF unit: {unit}")


@xl.register()
@xl.validate_args
def DAY(serial_number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    """
    Returns the day of month (1..31) from a date serial.
    """
    dt = date_utils.number_to_datetime(float(serial_number))
    return float(dt.day)


@xl.register()
@xl.validate_args
def DAYS(
    end_date: func_xltypes.XlNumber,
    start_date: func_xltypes.XlNumber
) -> func_xltypes.XlNumber:
    """
    Returns the number of days (end_date - start_date).
    """
    return float(end_date - start_date)


@xl.register()
@xl.validate_args
def EDATE(
    start_date: func_xltypes.XlNumber,
    months: func_xltypes.XlNumber
) -> func_xltypes.XlNumber:
    """
    Returns the serial for a date that is 'months' before/after start_date.
    """
    dt_start = date_utils.number_to_datetime(float(start_date))
    m = int(months)
    result_dt = dt_start + relativedelta(months=m)

    if result_dt <= date_utils.EXCEL_EPOCH:
        raise xlerrors.NumExcelError(f"Resulting date is before {date_utils.EXCEL_EPOCH}")

    return date_utils.datetime_to_number(result_dt)


@xl.register()
@xl.validate_args
def EOMONTH(
    start_date: func_xltypes.XlNumber,
    months: func_xltypes.XlNumber
) -> func_xltypes.XlNumber:
    """
    Returns the serial for the last day of the month 'months' before/after start_date.
    """
    dt_start = date_utils.number_to_datetime(float(start_date))
    m = int(months)
    candidate = dt_start + relativedelta(months=m)

    if candidate <= date_utils.EXCEL_EPOCH:
        raise xlerrors.NumExcelError(f"Resulting date is before {date_utils.EXCEL_EPOCH}")

    # Move to last day of that month
    last_day_dt = candidate + relativedelta(day=31)
    return date_utils.datetime_to_number(last_day_dt)


@xl.register()
@xl.validate_args
def ISOWEEKNUM(serial_number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    """
    Returns the ISO week number of the given date.
    """
    dt = date_utils.number_to_datetime(float(serial_number))
    # For Python >= 3.9, can do dt.isocalendar().week
    return float(dt.isocalendar()[1])


@xl.register()
@xl.validate_args
def MONTH(serial_number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    """
    Returns the month (1..12) of the given date serial.
    """
    dt = date_utils.number_to_datetime(float(serial_number))
    return float(dt.month)


@xl.register()
def NOW() -> func_xltypes.XlNumber:
    """
    Returns the Excel serial for the current date/time.
    """
    dt_now = _now()
    return date_utils.datetime_to_number(dt_now)


@xl.register()
def TODAY() -> func_xltypes.XlNumber:
    """
    Returns the Excel serial for today's date (midnight).
    """
    dt_now = _now()
    dt_midnight = dt_now.replace(hour=0, minute=0, second=0, microsecond=0)
    return date_utils.datetime_to_number(dt_midnight)


@xl.register()
@xl.validate_args
def WEEKDAY(
    serial_number: func_xltypes.XlNumber,
    return_type: func_xltypes.XlNumber = None
) -> func_xltypes.XlNumber:
    """
    Returns the day of the week for the given date serial, depending on return_type.
    Default is 1=Sunday..7=Saturday if omitted.
    """
    dt = date_utils.number_to_datetime(float(serial_number))
    weekday_python = dt.weekday()  # Mon=0..Sun=6

    if return_type is None:
        rtype = 1
    else:
        rtype = int(return_type)

    # same mapping logic as before
    if rtype == 1:
        mapping = (2, 3, 4, 5, 6, 7, 1)  # 1=Sunday..7=Saturday
    elif rtype == 2:
        mapping = (1, 2, 3, 4, 5, 6, 7)  # 1=Mon..7=Sun
    elif rtype == 3:
        mapping = (0, 1, 2, 3, 4, 5, 6)  # 0=Mon..6=Sun
    elif rtype == 11:
        mapping = (1, 2, 3, 4, 5, 6, 7)  # 1=Mon..7=Sun
    elif rtype == 12:
        mapping = (7, 1, 2, 3, 4, 5, 6)  # 1=Tue..7=Mon
    elif rtype == 13:
        mapping = (6, 7, 1, 2, 3, 4, 5)  # 1=Wed..7=Tue
    elif rtype == 14:
        mapping = (5, 6, 7, 1, 2, 3, 4)  # 1=Thu..7=Wed
    elif rtype == 15:
        mapping = (4, 5, 6, 7, 1, 2, 3)  # 1=Fri..7=Thu
    elif rtype == 16:
        mapping = (3, 4, 5, 6, 7, 1, 2)  # 1=Sat..7=Fri
    elif rtype == 17:
        mapping = (2, 3, 4, 5, 6, 7, 1)  # 1=Sun..7=Sat
    else:
        raise xlerrors.NumExcelError(
            f"Invalid WEEKDAY return_type: {rtype}. Must be 1,2,3,11..17 or omitted."
        )

    return float(mapping[weekday_python])


@xl.register()
@xl.validate_args
def YEAR(serial_number: func_xltypes.XlNumber) -> func_xltypes.XlNumber:
    """
    Returns the year (>=1900..<=9999) of the date serial.
    """
    dt = date_utils.number_to_datetime(float(serial_number))
    y = dt.year
    if y < 1900 or y > 9999:
        raise xlerrors.ValueExcelError(
            f"Year {y} must be between 1900 and 9999."
        )
    return float(y)


@xl.register()
@xl.validate_args
def YEARFRAC(
    start_date: func_xltypes.XlNumber,
    end_date: func_xltypes.XlNumber,
    basis: func_xltypes.XlNumber = 0
) -> func_xltypes.XlNumber:
    """
    Returns the fraction of the year between two date serials, given a 'basis'.
    """
    s = float(start_date)
    e = float(end_date)

    if s < date_utils.datetime_to_number(date_utils.EXCEL_EPOCH):
        raise xlerrors.ValueExcelError(
            f"start_date {s} is before {date_utils.EXCEL_EPOCH}"
        )
    if e < date_utils.datetime_to_number(date_utils.EXCEL_EPOCH):
        raise xlerrors.ValueExcelError(
            f"end_date {e} is before {date_utils.EXCEL_EPOCH}"
        )

    if s > e:
        # swap
        s, e = e, s

    # Convert to python datetime for some day-count routines
    sdt = date_utils.number_to_datetime(s)
    edt = date_utils.number_to_datetime(e)
    b = int(basis)

    if b == 0:  # US 30/360
        return float(yearfrac.yearfrac(sdt, edt, '30e360_matu'))
    elif b == 1:  # Actual/actual
        return float(yearfrac.yearfrac(sdt, edt, 'act_afb'))
    elif b == 2:  # Actual/360
        days_diff = (edt - sdt).days
        return float(days_diff / 360)
    elif b == 3:  # Actual/365
        days_diff = (edt - sdt).days
        return float(days_diff / 365)
    elif b == 4:  # Eurobond 30/360
        return float(yearfrac.yearfrac(sdt, edt, '30e360'))

    raise xlerrors.ValueExcelError(
        f"YEARFRAC: invalid basis {basis} (must be 0..4)."
    )
