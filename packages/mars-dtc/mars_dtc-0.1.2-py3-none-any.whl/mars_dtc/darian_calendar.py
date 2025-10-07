# ---------------- Imports ----------------
from mars_dtc.base_calendar import BaseCalendar


# ---------------- Classes and functions ----------------
class DarianCalendar(BaseCalendar):
    REGYEAR_MONTH_LENGTHS = [
        28, 28, 28, 28, 28, 27,
        28, 28, 28, 28, 28, 27,
        28, 28, 28, 28, 28, 27,
        28, 28, 28, 28, 28, 27
    ]

    MONTH_NAMES = {
        1: "Sagittarius", 2: "Dhanus", 3: "Capricornus", 4: "Makara",
        5: "Aquarius", 6: "Kumbha", 7: "Pisces", 8: "Mina",
        9: "Aries", 10: "Mesha", 11: "Taurus", 12: "Rishabha",
        13: "Gemini", 14: "Mithuna", 15: "Cancer", 16: "Karka",
        17: "Leo", 18: "Simha", 19: "Virgo", 20: "Kanya",
        21: "Libra", 22: "Tula", 23: "Scorpius", 24: "Vrishika"
    }

    WEEK_DAYS = {
        1: "Sol Solis", 2: "Sol Lunae", 3: "Sol Martis",
        4: "Sol Mercurii", 5: "Sol Jovis", 6: "Sol Veneris", 7: "Sol Saturni"
    }

    def month_name(self, month: int, short=False):
        full = self.MONTH_NAMES.get(month, f"Month{month}")
        return full[:3] if short else full

    def weekday_name(self, weekday: int, short=False):
        full = self.WEEK_DAYS.get(weekday, f"Day{weekday}")
        if short:
            return full.replace("Sol ", "")[:3]
        return full

    def is_leap_year(self, year: int) -> bool:
        """
        Leap year check.
        """
        if year % 500 == 0:
            return True  # 669
        if year % 100 == 0:
            return False  # 668
        if year % 10 == 0:
            return True  # 669
        if year % 2 == 0:
            return False  # 668
        return True

    def month_lengths(self, year: int) -> list[int]:
        """
        Modify REGYEAR_MONTH_LENGTHS if leap year.
        """
        validated_month_lengths = self.REGYEAR_MONTH_LENGTHS.copy()
        if self.is_leap_year(year):
            validated_month_lengths[-1] = 28
        return validated_month_lengths

    def validate_date(self, year: int, month: int, sol: int):
        validated_month_lengths = self.month_lengths(year)
        if not (1 <= month <= len(validated_month_lengths)):
            raise ValueError("Invalid month")

        # Sol check
        max_sol = validated_month_lengths[month - 1]
        if not (1 <= sol <= max_sol):

            if month == 24:
                if self.is_leap_year(year):
                    raise ValueError(
                        f"Invalid sol {sol} for month 24. "
                        f"Leap year {year} has only {max_sol} sols in this month."
                    )
                else:
                    raise ValueError(
                        f"Invalid sol {sol} for month 24. "
                        f"Year {year} is not a leap year, so this month has only {max_sol} sols."
                    )
            else:
                raise ValueError(
                    f"Invalid sol {sol} for month {month}. "
                    f"Valid range is 1–{max_sol}."
                )

    def to_ordinal(self, year: int, month: int, sol: int) -> int:
        # Count all sols in complete prior years
        total = 0

        if year >= 0:
            # Count all sols in years before this one
            for y in range(0, year):
                total += sum(self.month_lengths(y))
        else:
            # For negative years, count backward — subtract sols from year up to -1
            for y in range(year, 0):
                total -= sum(self.month_lengths(y))

        # Add sols within current year
        lengths = self.month_lengths(year)
        sols_before = sum(lengths[:month - 1]) + (sol - 1)

        return total + sols_before

    def from_ordinal(self, ordinal: int):

        # Find year
        year = 0
        remaining = ordinal  # how far (in sols) the target date is from year 0

        # Handle negative ordinals (years before year 0)
        if ordinal < 0:  # If the ordinal value is negative
            while True:  # Keep looping backward through years until we find the correct one
                # Get month lengths for the previous year (year - 1)
                lengths = self.month_lengths(year - 1)
                # Count how many sols that previous year has (668 or 669)
                sols_in_year = sum(lengths)

                # Check if moving back one more year would bring us to or past the target ordinal

                if remaining + sols_in_year >= 0:  # If adding this year's sols brings us to or past zero, we've found the target year
                    year -= 1  # # Move back exactly one year
                    # Adjust `remaining`` to represent the sol offset within that year
                    remaining += sols_in_year
                    break

                # Move one full year backward (increase remaining toward zero)
                remaining += sols_in_year
                year -= 1  # Decrease the year counter as we go further into negative years
        else:
            while True:
                lengths = self.month_lengths(year)
                sols_in_year = sum(lengths)
                if remaining < sols_in_year:
                    break
                remaining -= sols_in_year
                year += 1

        # Find month and sol
        lengths = self.month_lengths(year)
        month = 1
        while remaining >= lengths[month - 1]:
            remaining -= lengths[month - 1]
            month += 1

        sol = remaining + 1
        return year, month, sol


if __name__ == "__main__":

    c = DarianCalendar()
