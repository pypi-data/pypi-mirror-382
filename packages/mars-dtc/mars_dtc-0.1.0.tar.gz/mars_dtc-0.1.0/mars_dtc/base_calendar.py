# ---------------- Imports ----------------
from abc import ABC, abstractmethod


# ---------------- Classes and functions ----------------
class BaseCalendar(ABC):
    """
    Base class for all calendar systems. Trying to instantiate a calendar
    inheriting from BaseCalendar without all the methods below will result in
    an error.
    """

    @abstractmethod
    def is_leap_year(self, year: int) -> bool:
        pass

    @abstractmethod
    def month_lengths(self, year: int) -> list[int]:
        """Return list of month lengths for a given year."""
        pass

    @abstractmethod
    def to_ordinal(self, year: int, month: int, sol: int) -> int:
        """Convert date to integer ordinal."""
        pass

    @abstractmethod
    def from_ordinal(self, ordinal: int):
        """Return (year, month, sol) tuple from an ordinal."""
        pass

    @abstractmethod
    def validate_date(self, year: int, month: int, sol: int):
        """Raise if the date is invalid for that calendar."""
        pass
