#!/usr/bin/env python3
"""
International Fixed Calendar (IFC) Converter CLI

Convert between Gregorian calendar and the International Fixed Calendar.

Usage:
    ifc                     # Show today's date in IFC
    ifc 2025-12-25          # Convert Gregorian date to IFC
    ifc --to-gregorian 7 15 2025   # Convert IFC (Sol 15, 2025) to Gregorian
    ifc --range 2025-01-01 2025-01-31  # Convert date range
    ifc --calendar 2025     # Show full year calendar
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import Optional, Tuple, NamedTuple

IFC_MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'Sol', 'July', 'August', 'September', 'October', 'November', 'December'
]

IFC_WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


class IFCDate(NamedTuple):
    year: int
    month: Optional[int]
    day: Optional[int]
    special: Optional[str]
    weekday: Optional[str]

    def __str__(self):
        if self.special:
            return f"{self.special}, {self.year}"
        return f"{IFC_MONTHS[self.month - 1]} {self.day}, {self.year} ({self.weekday})"


def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def day_of_year(date: datetime) -> int:
    return (date - datetime(date.year, 1, 1)).days + 1


def gregorian_to_ifc(date: datetime) -> IFCDate:
    """Convert a Gregorian date to IFC date."""
    year = date.year
    doy = day_of_year(date)
    leap = is_leap_year(year)

    # Year Day (last day of year)
    if doy == (366 if leap else 365):
        return IFCDate(year=year, month=None, day=None, special='Year Day', weekday=None)

    # Leap Day (day 169 in leap years)
    if leap and doy == 169:
        return IFCDate(year=year, month=None, day=None, special='Leap Day', weekday=None)

    # Adjust for leap day
    adjusted_day = doy
    if leap and doy > 169:
        adjusted_day = doy - 1

    # Calculate month and day
    month = (adjusted_day - 1) // 28 + 1
    day = ((adjusted_day - 1) % 28) + 1
    weekday_idx = (day - 1) % 7

    return IFCDate(
        year=year,
        month=month,
        day=day,
        special=None,
        weekday=IFC_WEEKDAYS[weekday_idx]
    )


def ifc_to_gregorian(year: int, month: Optional[int] = None, day: Optional[int] = None,
                      special: Optional[str] = None) -> datetime:
    """Convert an IFC date to Gregorian date."""
    leap = is_leap_year(year)

    if special == 'year':
        doy = 366 if leap else 365
    elif special == 'leap':
        if not leap:
            raise ValueError(f"{year} is not a leap year")
        doy = 169
    else:
        doy = (month - 1) * 28 + day
        if leap and month > 6:
            doy += 1

    return datetime(year, 1, 1) + timedelta(days=doy - 1)


def print_calendar(year: int):
    """Print a full IFC calendar for the given year."""
    leap = is_leap_year(year)

    print(f"\n{'=' * 60}")
    print(f"  INTERNATIONAL FIXED CALENDAR - {year}")
    print(f"  {'(Leap Year)' if leap else ''}")
    print(f"{'=' * 60}\n")

    for month in range(1, 14):
        month_name = IFC_MONTHS[month - 1]
        marker = " ***" if month == 7 else ""  # Highlight Sol
        print(f"  {month_name}{marker}")
        print("  " + "-" * 28)
        print("  Sun Mon Tue Wed Thu Fri Sat")

        for week in range(4):
            row = "  "
            for day_in_week in range(7):
                day = week * 7 + day_in_week + 1
                row += f"{day:3} "
            print(row)

        # Show Leap Day after June
        if month == 6 and leap:
            print("\n  >>> LEAP DAY <<<\n")

        print()

    print("  YEAR DAY")
    print("  " + "-" * 28)
    print("  Worldwide Holiday - Outside Weekly Cycle\n")
    print(f"{'=' * 60}\n")


def print_range(start: datetime, end: datetime):
    """Print date range conversion."""
    print(f"\n{'Gregorian':<25} {'Fixed Calendar':<30}")
    print("-" * 55)

    current = start
    while current <= end:
        ifc = gregorian_to_ifc(current)
        greg_str = current.strftime("%b %d, %Y")
        if ifc.special:
            ifc_str = f"** {ifc.special} **"
        else:
            ifc_str = f"{IFC_MONTHS[ifc.month - 1]} {ifc.day}"
        print(f"{greg_str:<25} {ifc_str:<30}")
        current += timedelta(days=1)
    print()


def parse_date(date_str: str) -> datetime:
    """Parse various date formats."""
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: {date_str}")


def main():
    parser = argparse.ArgumentParser(
        description='International Fixed Calendar Converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ifc                           Show today in IFC
  ifc 2025-12-25                Convert Gregorian to IFC
  ifc --to-gregorian 7 15 2025  Convert Sol 15, 2025 to Gregorian
  ifc --range 2025-01-01 2025-01-31  Show date range
  ifc --calendar 2025           Print full year calendar
  ifc --months                  List all IFC months
        """
    )

    parser.add_argument('date', nargs='?', help='Gregorian date (YYYY-MM-DD)')
    parser.add_argument('--to-gregorian', '-g', nargs=3, metavar=('MONTH', 'DAY', 'YEAR'),
                        help='Convert IFC to Gregorian (month day year)')
    parser.add_argument('--range', '-r', nargs=2, metavar=('START', 'END'),
                        help='Convert date range')
    parser.add_argument('--calendar', '-c', type=int, metavar='YEAR',
                        help='Print full year calendar')
    parser.add_argument('--months', '-m', action='store_true',
                        help='List all IFC months')
    parser.add_argument('--leap-day', '-l', type=int, metavar='YEAR',
                        help='Show Leap Day for given year')
    parser.add_argument('--year-day', '-y', type=int, metavar='YEAR',
                        help='Show Year Day for given year')

    args = parser.parse_args()

    # List months
    if args.months:
        print("\nInternational Fixed Calendar Months:")
        print("-" * 35)
        for i, month in enumerate(IFC_MONTHS, 1):
            marker = " (new month)" if month == "Sol" else ""
            print(f"  {i:2}. {month}{marker}")
        print("\nPlus: Leap Day (after June) and Year Day (end of year)")
        print()
        return

    # Print calendar
    if args.calendar:
        print_calendar(args.calendar)
        return

    # Date range
    if args.range:
        start = parse_date(args.range[0])
        end = parse_date(args.range[1])
        if (end - start).days > 366:
            print("Error: Range limited to 366 days", file=sys.stderr)
            sys.exit(1)
        print_range(start, end)
        return

    # IFC to Gregorian
    if args.to_gregorian:
        month_str, day_str, year_str = args.to_gregorian
        year = int(year_str)

        # Handle special days
        if month_str.lower() in ('leap', 'leapday', 'leap-day'):
            try:
                result = ifc_to_gregorian(year, special='leap')
                print(f"\nLeap Day {year} = {result.strftime('%A, %B %d, %Y')}\n")
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            return

        if month_str.lower() in ('year', 'yearday', 'year-day'):
            result = ifc_to_gregorian(year, special='year')
            print(f"\nYear Day {year} = {result.strftime('%A, %B %d, %Y')}\n")
            return

        # Parse month (name or number)
        try:
            month = int(month_str)
        except ValueError:
            month_lower = month_str.lower()
            try:
                month = next(i for i, m in enumerate(IFC_MONTHS, 1)
                           if m.lower().startswith(month_lower))
            except StopIteration:
                print(f"Error: Unknown month '{month_str}'", file=sys.stderr)
                sys.exit(1)

        day = int(day_str)
        if not 1 <= day <= 28:
            print("Error: Day must be between 1 and 28", file=sys.stderr)
            sys.exit(1)

        result = ifc_to_gregorian(year, month, day)
        ifc_weekday = IFC_WEEKDAYS[(day - 1) % 7]
        print(f"\n{IFC_MONTHS[month-1]} {day}, {year} ({ifc_weekday})")
        print(f"= {result.strftime('%A, %B %d, %Y')}\n")
        return

    # Leap Day
    if args.leap_day:
        year = args.leap_day
        if not is_leap_year(year):
            print(f"Error: {year} is not a leap year", file=sys.stderr)
            sys.exit(1)
        result = ifc_to_gregorian(year, special='leap')
        print(f"\nLeap Day {year} = {result.strftime('%A, %B %d, %Y')}\n")
        return

    # Year Day
    if args.year_day:
        year = args.year_day
        result = ifc_to_gregorian(year, special='year')
        print(f"\nYear Day {year} = {result.strftime('%A, %B %d, %Y')}\n")
        return

    # Convert Gregorian to IFC
    if args.date:
        date = parse_date(args.date)
    else:
        date = datetime.now()

    ifc = gregorian_to_ifc(date)

    print(f"\nGregorian: {date.strftime('%A, %B %d, %Y')}")
    print(f"Fixed Cal: {ifc}")

    if ifc.special:
        print(f"           (Outside the weekly cycle)")
    print()


if __name__ == '__main__':
    main()
