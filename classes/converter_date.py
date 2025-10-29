import datetime as dt
import re

_DOT_DATE = re.compile(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{4})")

def parse_dt(value):
    """Acepta None, datetime/date, 'dd.mm.yyyy' o ISO. Devuelve datetime o None."""
    if not value:
        return None
    if isinstance(value, dt.datetime):
        return value
    if isinstance(value, str):
        parts = value.split(".")
        if len(parts) == 3:
            day, month, year = map(int, parts)
            return dt.datetime(year, month, day)
    s = str(value).strip()

    m = _DOT_DATE.match(s)  # dd.mm.yyyy
    if m:
        d, mth, y = map(int, m.groups())
        return dt.datetime(y, mth, d)

    try:
        return dt.datetime.date(s.replace("Z", "+00:00"))
    except Exception:
        return None