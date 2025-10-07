# ---------------- Imports ----------------
import json
import math
import re
from functools import total_ordering

import yaml


from mars_dtc.darian_calendar import DarianCalendar


# ---------------- Classes and functions ----------------
@total_ordering
class MarsDate:

    def __init__(self, year: int, month: int, sol: int, calendar=None):

        # Allow any registered calendar, fall back to a Darian
        self.calendar = calendar or DarianCalendar()

        validated_month_lengths = self.calendar.month_lengths(year)
        if not (1 <= month <= len(validated_month_lengths)):
            raise ValueError(
                f"Month must be between 1 and {len(validated_month_lengths)}")
        if not (1 <= sol <= validated_month_lengths[month - 1]):
            raise ValueError(f"Invalid sol {sol} for month {month}")

        self.year = year
        self.month = month
        self.sol = sol

    # ----- Representations -----
    def __repr__(self):
        cname = getattr(self.calendar, "name",
                        lambda: self.calendar.__class__.__name__)()
        return f"{cname}Date({self.year}, {self.month}, {self.sol})"

    def __str__(self):
        return f"{self.year:03d}/{self.month:02d}/{self.sol:02d}"

    def __hash__(self):
        return hash((self.year, self.month, self.sol, self.calendar.__class__.__name__))

    # ----- Comparisons -----

    def __eq__(self, other):
        return (
            isinstance(other, MarsDate)
            and self.calendar.__class__ == other.calendar.__class__
            and (self.year, self.month, self.sol) == (other.year, other.month, other.sol)
        )

    def __lt__(self, other):
        if not isinstance(other, MarsDate):
            return NotImplemented
        if self.calendar.__class__ != other.calendar.__class__:
            raise TypeError(
                "Cannot compare MarsDate objects with different calendars")
        return self.to_ordinal() < other.to_ordinal()

    def __le__(self, other):
        if not isinstance(other, MarsDate):
            return NotImplemented
        if self.calendar.__class__ != other.calendar.__class__:
            raise TypeError(
                "Cannot compare MarsDate objects with different calendars")
        return self.to_ordinal() <= other.to_ordinal()

    def __gt__(self, other):
        if not isinstance(other, MarsDate):
            return NotImplemented
        if self.calendar.__class__ != other.calendar.__class__:
            raise TypeError(
                "Cannot compare MarsDate objects with different calendars")
        return self.to_ordinal() > other.to_ordinal()

    def __ge__(self, other):
        if not isinstance(other, MarsDate):
            return NotImplemented
        if self.calendar.__class__ != other.calendar.__class__:
            raise TypeError(
                "Cannot compare MarsDate objects with different calendars")
        return self.to_ordinal() >= other.to_ordinal()

    # ----- Arithmetic -----

    def __add__(self, other):
        if isinstance(other, MarsTimedelta):
            new_ord = self.to_ordinal() + other.sols
            return MarsDate.from_ordinal(int(new_ord), calendar=self.calendar)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, MarsTimedelta):
            new_ord = self.to_ordinal() - other.sols
            return MarsDate.from_ordinal(int(new_ord), calendar=self.calendar)
        elif isinstance(other, MarsDate):
            if self.calendar.__class__ != other.calendar.__class__:
                raise TypeError(
                    "Cannot subtract MarsDate objects of different calendars")
            return MarsTimedelta(self.to_ordinal() - other.to_ordinal())
        return NotImplemented

    # ----- Leap logic -----

    def is_leap_year(self) -> bool:
        return self.calendar.is_leap_year(self.year)

    # ----- Conversion -----

    def to_ordinal(self) -> int:

        return self.calendar.to_ordinal(self.year, self.month, self.sol)

    def to_ordinal_float(self) -> float:

        return float(self.to_ordinal())

    @classmethod
    def from_ordinal(cls, ordinal: int | float, calendar=None) -> "MarsDate":
        cal = calendar or DarianCalendar()
        year, month, sol = cal.from_ordinal(int(ordinal)) 
        return cls(int(year), int(month), int(sol), calendar=cal)

    @classmethod
    def from_string(cls, s: str, calendar=None) -> "MarsDate":
        """
        Parse strings like '0001/01/01', '0001-01-01', '0001.01.01',
        and also negative years like '-0214/14/28' or '-214-14-28'.
        """
        cal = calendar or DarianCalendar()
        s = s.strip()

        # Match optional leading minus, then digits, then separators
        match = re.match(r'^(-?\d+)[/.\-\s](\d+)[/.\-\s](\d+)$', s)
        if not match:
            raise ValueError(f"Invalid MarsDate string: {s}")

        year, month, sol = map(int, match.groups())
        return cls(year, month, sol, calendar=cal)

    def isoformat(self) -> str:

        return f"{self.year:+05d}-{self.month:02d}-{self.sol:02d}"

    # ----- Serialization -----

    def to_dict(self):
        return {
            "year": self.year,
            "month": self.month,
            "sol": self.sol,
            "calendar": self.calendar.__class__.__name__,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict, calendar=None):

        cal = calendar or DarianCalendar()
        return cls(
            data["year"],
            data["month"],
            data["sol"],
            calendar=cal,
        )

    @classmethod
    def from_json(cls, json_str: str, calendar=None):

        data = json.loads(json_str)
        return cls.from_dict(data, calendar=calendar)

    @classmethod
    def from_yaml(cls, yaml_str: str, calendar=None):

        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data, calendar=calendar)

    # ----- Formatting -----

    def format(self, fmt: str = "%Y/%m/%d") -> str:
        """
        Supported codes:
        %Y = full year (signed)
        %y = 2-digit year
        %m = numeric month (01–24)
        %B = full month name
        %b = abbreviated month name
        %d = sol (01–28)
        %A = full weekday name
        %a = abbreviated weekday name
        """
        year, month, sol = self.year, self.month, self.sol
        wd = self.weekday()

        # Retrieve names from calendar
        month_full = self.calendar.month_name(month)
        month_abbr = self.calendar.month_name(month, short=True)
        weekday_full = self.calendar.weekday_name(wd)
        weekday_abbr = self.calendar.weekday_name(wd, short=True)

        replacements = {
            "%Y": f"{year:+04d}" if year < 0 else f"{year:03d}",
            "%y": f"{abs(year) % 100:02d}",
            "%m": f"{month:02d}",
            "%B": month_full,
            "%b": month_abbr,
            "%d": f"{sol:02d}",
            "%A": weekday_full,
            "%a": weekday_abbr,
        }

        result = fmt
        for code, val in replacements.items():
            result = result.replace(code, val)
        return result

    def weekday(self) -> int:

        return (self.to_ordinal() % 7) + 1

    def weekday_name(self, short: bool = False) -> str:
        """
        Return the full or abbreviated weekday name
        """
        wd = self.weekday()
        return self.calendar.weekday_name(wd, short=short)

    # ----- Arithmetic helpers -----

    def add_sols(self, n: int) -> "MarsDate":
        return MarsDate.from_ordinal(self.to_ordinal() + n, calendar=self.calendar)

    def add_months(self, n: int) -> "MarsDate":

        if not isinstance(n, int):
            raise TypeError("Number of months must be an integer")

        # Compute new month/year combination
        total_months = (self.year * 24) + (self.month - 1) + n
        new_year, new_month_index = divmod(total_months, 24)
        new_month = new_month_index + 1

        # Get new month's length (account for leap year)
        month_lengths = self.calendar.month_lengths(new_year)
        max_sol = month_lengths[new_month - 1]

        # Clamp sol to avoid invalid days
        new_sol = min(self.sol, max_sol)

        return MarsDate(new_year, new_month, new_sol, calendar=self.calendar)

    def add_years(self, n: int) -> "MarsDate":

        if not isinstance(n, int):
            raise TypeError("Number of years must be an integer")

        new_year = self.year + n

        # Get month lengths for the new year
        month_lengths = self.calendar.month_lengths(new_year)
        max_sol = month_lengths[self.month - 1]

        # Clamp sol if target month shorter
        new_sol = min(self.sol, max_sol)

        return MarsDate(new_year, self.month, new_sol, calendar=self.calendar)

    # ----- Rounding -----

    def floor(self, unit: str) -> "MarsDate":

        unit = unit.lower()
        if unit == "sol":
            return MarsDate(self.year, self.month, self.sol, calendar=self.calendar)

        if unit == "month":
            # First sol of current month
            return MarsDate(self.year, self.month, 1, calendar=self.calendar)

        if unit == "year":
            # First sol of first month
            return MarsDate(self.year, 1, 1, calendar=self.calendar)

        raise ValueError("Unit must be one of: 'sol', 'month', 'year'")

    def ceil(self, unit: str) -> "MarsDate":

        unit = unit.lower()
        if unit == "sol":
            return MarsDate(self.year, self.month, self.sol, calendar=self.calendar)

        if unit == "month":
            # Last sol of the current month
            month_lengths = self.calendar.month_lengths(self.year)
            last_sol = month_lengths[self.month - 1]
            return MarsDate(self.year, self.month, last_sol, calendar=self.calendar)

        if unit == "year":
            # Last sol of the last month
            month_lengths = self.calendar.month_lengths(self.year)
            last_sol = month_lengths[-1]
            return MarsDate(self.year, len(month_lengths), last_sol, calendar=self.calendar)

        raise ValueError("Unit must be one of: 'sol', 'month', 'year'")

    def round(self, unit: str) -> "MarsDate":

        unit = unit.lower()
        if unit not in ("month", "year"):
            raise ValueError("Unit must be 'month' or 'year'")

        # Round to nearest month
        if unit == "month":
            month_lengths = self.calendar.month_lengths(self.year)
            mid_sol = (month_lengths[self.month - 1] + 1) / 2
            if self.sol < mid_sol:
                return self.floor("month")
            else:
                return self.add_months(1).floor("month")

        # Round to nearest year
        if unit == "year":
            sols_in_year = sum(self.calendar.month_lengths(self.year))
            start_of_year = MarsDate(self.year, 1, 1, calendar=self.calendar)
            sols_from_start = self.to_ordinal() - start_of_year.to_ordinal()
            if sols_from_start < sols_in_year / 2:
                return self.floor("year")
            else:
                return MarsDate(self.year + 1, 1, 1, calendar=self.calendar)


@total_ordering
class MarsDateTime(MarsDate):

    SECONDS_PER_SOL = 24 * 60 * 60

    def __init__(self, year, month, sol, hour=0, minute=0, second=0, calendar=None):
        super().__init__(year, month, sol, calendar=calendar)

        if not (0 <= hour < 24):
            raise ValueError("hour must be in [0, 24)")
        if not (0 <= minute < 60):
            raise ValueError("minute must be in [0, 60)")
        if not (0 <= second < 60):
            raise ValueError("second must be in [0, 60)")

        self.hour = int(hour)
        self.minute = int(minute)
        self.second = int(second)

    # ----- Representations -----
    def __repr__(self):
        cname = getattr(self.calendar, "name",
                        lambda: self.calendar.__class__.__name__)()
        return (f"{cname}DateTime({self.year}, {self.month}, {self.sol}, "
                f"{self.hour:02d}, {self.minute:02d}, {self.second:02d})")

    def __str__(self):
        return f"{self.year:03d}/{self.month:02d}/{self.sol:02d} {self.hour:02d}:{self.minute:02d}:{self.second:02d}"

    # ----- Conversion -----
    def to_ordinal_float(self) -> float:

        base = self.calendar.to_ordinal(self.year, self.month, self.sol)
        fraction = (self.hour * 3600 + self.minute * 60 +
                    self.second) / self.SECONDS_PER_SOL
        return base + fraction

    @classmethod
    def from_ordinal_float(cls, ordinal: float, calendar=None):

        base_sol = int(ordinal)
        frac = ordinal - base_sol
        base_date = MarsDate.from_ordinal(base_sol, calendar=calendar)
        total_seconds = frac * cls.SECONDS_PER_SOL
        hour = int(total_seconds // 3600)
        minute = int((total_seconds % 3600) // 60)
        second = int(total_seconds % 60)
        return cls(base_date.year, base_date.month, base_date.sol, hour, minute, second, calendar=base_date.calendar)

    # ----- Comparisons -----
    def __eq__(self, other):
        if not isinstance(other, MarsDateTime):
            return False
        return math.isclose(self.to_ordinal_float(), other.to_ordinal_float(), rel_tol=1e-9)

    def __lt__(self, other):
        if not isinstance(other, MarsDateTime):
            return NotImplemented
        if self.calendar.__class__ != other.calendar.__class__:
            raise TypeError(
                "Cannot compare MarsDateTime objects of different calendars")
        return self.to_ordinal_float() < other.to_ordinal_float()

    # ----- Arithmetic -----
    def __sub__(self, other):
        if isinstance(other, MarsDateTime):
            if self.calendar.__class__ != other.calendar.__class__:
                raise TypeError(
                    "Cannot subtract MarsDateTime of different calendars")
            diff_in_sols = self.to_ordinal_float() - other.to_ordinal_float()
            return MarsTimedelta(diff_in_sols)
        elif isinstance(other, MarsTimedelta):
            return MarsDateTime.from_ordinal_float(self.to_ordinal_float() - other.sols, calendar=self.calendar)
        return NotImplemented

    def __add__(self, other):

        if isinstance(other, MarsTimedelta):
            new_ordinal = self.to_ordinal_float() + other.sols
            return MarsDateTime.from_ordinal_float(new_ordinal, calendar=self.calendar)
        return NotImplemented

    # ----- Floor/Ceil/Round -----
    def floor(self, unit: str) -> "MarsDateTime":

        unit = unit.lower()
        if unit == "second":
            return MarsDateTime(self.year, self.month, self.sol, self.hour, self.minute, self.second, calendar=self.calendar)
        if unit == "minute":
            return MarsDateTime(self.year, self.month, self.sol, self.hour, self.minute, 0, calendar=self.calendar)
        if unit == "hour":
            return MarsDateTime(self.year, self.month, self.sol, self.hour, 0, 0, calendar=self.calendar)
        if unit in ("sol", "month", "year"):
            base = super().floor(unit)
            return MarsDateTime(base.year, base.month, base.sol, 0, 0, 0, calendar=self.calendar)
        raise ValueError(
            "Unit must be one of: 'second', 'minute', 'hour', 'sol', 'month', 'year'")

    def ceil(self, unit: str) -> "MarsDateTime":

        unit = unit.lower()
        if unit == "second":
            return self
        if unit == "minute":
            carry = self.second > 0
            new_min = self.minute + carry
            new_hr = self.hour
            if new_min >= 60:
                new_min = 0
                new_hr += 1
            return MarsDateTime(self.year, self.month, self.sol, new_hr, new_min, 0, calendar=self.calendar)
        if unit == "hour":
            carry = (self.minute > 0 or self.second > 0)
            new_hr = self.hour + carry
            return MarsDateTime(self.year, self.month, self.sol, new_hr, 0, 0, calendar=self.calendar)
        if unit in ("sol", "month", "year"):
            base = super().ceil(unit)
            return MarsDateTime(base.year, base.month, base.sol, 23, 59, 59, calendar=self.calendar)
        raise ValueError(
            "Unit must be one of: 'second', 'minute', 'hour', 'sol', 'month', 'year'")

    def round(self, unit: str) -> "MarsDateTime":

        unit = unit.lower()
        if unit == "second":
            return self
        if unit == "minute":
            if self.second >= 30:
                minute = self.minute + 1
                hour = self.hour
                if minute == 60:
                    minute = 0
                    hour += 1
                return MarsDateTime(self.year, self.month, self.sol, hour, minute, 0, calendar=self.calendar)
            else:
                return MarsDateTime(self.year, self.month, self.sol, self.hour, self.minute, 0, calendar=self.calendar)
        if unit == "hour":
            total_seconds = self.hour * 3600 + self.minute * 60 + self.second
            if total_seconds % 3600 >= 1800:
                return MarsDateTime(self.year, self.month, self.sol, self.hour + 1, 0, 0, calendar=self.calendar)
            else:
                return MarsDateTime(self.year, self.month, self.sol, self.hour, 0, 0, calendar=self.calendar)
        if unit in ("sol", "month", "year"):
            return super().round(unit)
        raise ValueError(
            "Unit must be one of: 'second', 'minute', 'hour', 'sol', 'month', 'year'")

    # ----- Serialization -----
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
        })
        return base

    @classmethod
    def from_dict(cls, data, calendar=None):
        return cls(
            data["year"],
            data["month"],
            data["sol"],
            data.get("hour", 0),
            data.get("minute", 0),
            data.get("second", 0),
            calendar=calendar,
        )

    def isoformat(self):

        return f"{self.year:+05d}-{self.month:02d}-{self.sol:02d}T{self.hour:02d}:{self.minute:02d}:{self.second:02d}"


class MarsTimedelta:

    def __init__(self, sols: int):
        if not isinstance(sols, (int, float)):
            raise TypeError("sols must be an integer or float")
        self.sols = float(sols)

    def __repr__(self):
        sign = "+" if self.sols >= 0 else "-"
        return f"MarsTimedelta({sign}{abs(self.sols)} sols)"

    def __eq__(self, other):
        if not isinstance(other, MarsTimedelta):
            return NotImplemented
        return self.sols == other.sols

    def __neg__(self):
        return MarsTimedelta(-self.sols)

    def __add__(self, other):
        if isinstance(other, MarsTimedelta):
            return MarsTimedelta(self.sols + other.sols)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, MarsTimedelta):
            return MarsTimedelta(self.sols - other.sols)
        return NotImplemented



# ---------------- Public API Re-Exports ----------------
# Late imports to avoid circular dependencies
from mars_dtc.pandas_ext import MarsDateArray, MarsDateDtype
from mars_dtc.utils import mars_date_range, get_martian_week, get_sol_of_year

__all__ = [
    "MarsDate",
    "MarsDateTime",
    "MarsTimedelta",
    "MarsDateArray",
    "MarsDateDtype",
    "mars_date_range",
    "get_martian_week",
    "get_sol_of_year",
    "plot",
]
