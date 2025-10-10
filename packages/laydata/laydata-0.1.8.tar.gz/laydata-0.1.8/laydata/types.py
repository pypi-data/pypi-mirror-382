from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date, timezone, timedelta
from typing import Any, List


@dataclass(frozen=True)
class Attachment:
    """
    Represents an attachment source. `source` may be a local file path or an http(s) URL.
    The client will decide how to send it (multipart for file path, fileUrl for remote).
    """
    source: str

    def is_url(self) -> bool:
        return self.source.startswith("http://") or self.source.startswith("https://")


@dataclass(frozen=True)
class Date:
    """
    Flexible date/time wrapper with optional timezone, defaulting to GMT+3.
    Accepts:
    - datetime
    - date
    - str in common formats (e.g., YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, 'YYYY/MM/DD', 'DD.MM.YYYY', with optional 'Z')

    timezone examples: "GMT+3", "+03:00", "UTC-5", "-0500".
    """
    value: Any
    timezone: str = "GMT+3"

    def _parse_tz(self) -> timezone:
        s = self.timezone.strip().upper().replace("UTC", "").replace("GMT", "")
        if not s:
            s = "+0"
        sign = 1
        if s[0] == "+":
            sign = 1
            s = s[1:]
        elif s[0] == "-":
            sign = -1
            s = s[1:]
        # s can be '3', '03', '03:00', '0300'
        hours = 0
        minutes = 0
        if ":" in s:
            parts = s.split(":", 1)
            hours = int(parts[0])
            minutes = int(parts[1]) if parts[1] else 0
        elif len(s) in (3,4):
            # e.g., '300' or '0300'
            if len(s) == 3:
                hours = int(s[0])
                minutes = int(s[1:])
            else:
                hours = int(s[:2])
                minutes = int(s[2:])
        elif s:
            hours = int(s)
        offset = timedelta(hours=sign*hours, minutes=sign*minutes)
        return timezone(offset)

    def _parse_datetime(self) -> datetime:
        tzinfo = self._parse_tz()
        v = self.value
        if isinstance(v, datetime):
            if v.tzinfo is None:
                v = v.replace(tzinfo=tzinfo)
            else:
                v = v.astimezone(tzinfo)
            return v
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day, 0, 0, 0, tzinfo=tzinfo)
        if isinstance(v, str):
            s = v.strip()
            # Try common patterns
            fmts = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d.%m.%Y",
            ]
            for fmt in fmts:
                try:
                    dt = datetime.strptime(s, fmt)
                    if fmt.endswith("Z"):
                        dt = dt.replace(tzinfo=timezone.utc)
                    else:
                        dt = dt.replace(tzinfo=None)
                    # Attach provided tz if naive
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=tzinfo)
                    return dt
                except ValueError:
                    continue
            # Fallback: interpret as date only
            try:
                parts = s.split("-")
                if len(parts) == 3:
                    y, m, d = map(int, parts)
                    return datetime(y, m, d, 0, 0, 0, tzinfo=tzinfo)
            except Exception:
                pass
            raise ValueError(f"Unrecognized date format: {v}")
        raise TypeError(f"Unsupported Date.value type: {type(v)}")

    def to_utc_iso_millis_z(self) -> str:
        dt = self._parse_datetime()
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


@dataclass(frozen=True)
class SingleSelect:
    value: str


@dataclass(frozen=True)
class MultiSelect:
    values: List[str]
