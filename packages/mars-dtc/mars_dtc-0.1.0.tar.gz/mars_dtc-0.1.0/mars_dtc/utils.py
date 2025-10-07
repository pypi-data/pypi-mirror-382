# ---------------- Imports ----------------
from mars_dtc.darian_calendar import DarianCalendar
from mars_dtc.mars_dtc import MarsDate


# ---------------- Classes and functions ----------------
def mars_date_range(start, end, freq="sol", calendar=None):

    cal = calendar or DarianCalendar()

    # Convert strings to MarsDate if needed
    if isinstance(start, str):
        start = MarsDate.from_string(start, calendar=cal)
    if isinstance(end, str):
        end = MarsDate.from_string(end, calendar=cal)

    # Validate order
    if start > end:
        raise ValueError("start must be before or equal to end")

    freq = freq.lower()
    result = []

    current = start
    while current <= end:
        result.append(current)
        if freq == "sol":
            current = current.add_sols(1)
        elif freq == "month":
            current = current.add_months(1)
        elif freq == "year":
            current = current.add_years(1)
        else:
            raise ValueError("freq must be one of: 'sol', 'month', 'year'")

    return result


def get_martian_week(date: "MarsDate") -> int:

    if not isinstance(date, MarsDate):
        date = MarsDate.from_string(str(date))
    sols_from_year_start = date.to_ordinal() - MarsDate(date.year, 1, 1).to_ordinal()
    return sols_from_year_start // 7 + 1


def get_sol_of_year(date: "MarsDate") -> int:

    if not isinstance(date, MarsDate):
        date = MarsDate.from_string(str(date))
    start_of_year = MarsDate(date.year, 1, 1)
    return (date.to_ordinal() - start_of_year.to_ordinal()) + 1


# Also attach as a convenience method on MarsDate
def _sol_of_year_method(self) -> int:
    return get_sol_of_year(self)


MarsDate.sol_of_year = _sol_of_year_method


