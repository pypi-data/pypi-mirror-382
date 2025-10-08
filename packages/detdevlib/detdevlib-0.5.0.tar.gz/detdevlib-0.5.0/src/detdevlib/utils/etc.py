from datetime import date, datetime, timedelta

import pytz


def safe_int(x: str) -> int | None:
    """Converts a string to int if possible, otherwise returns None."""
    try:
        return int(x)
    except ValueError:
        return None


def clean_dict(d: dict) -> dict:
    """Removes all None values from a dictionary."""
    return {k: v for k, v in d.items() if v is not None}


def is_dst_adj_day(date_obj: date) -> bool:
    """Checks if a given date is a day when Daylight Saving Time (DST) adjustment occurs.

    Assumes Amsterdam locality.
    """
    next_date_obj = date_obj + timedelta(days=1)

    tz_amsterdam = pytz.timezone("Europe/Amsterdam")
    day_start = tz_amsterdam.localize(
        datetime(date_obj.year, date_obj.month, date_obj.day)
    )
    next_day_start = tz_amsterdam.localize(
        datetime(next_date_obj.year, next_date_obj.month, next_date_obj.day)
    )

    duration_of_day = next_day_start - day_start
    return duration_of_day != timedelta(hours=24)
