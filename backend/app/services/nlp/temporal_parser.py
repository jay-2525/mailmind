import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple


class TemporalParser:
    """
    Temporal and deadline extraction utility.
    Parses absolute and relative dates from email content.
    """

    WEEKDAYS = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }

    MONTHS = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9,
        "oct": 10, "nov": 11, "dec": 12
    }

    @classmethod
    def parse_deadline(cls, text: str, reference_time: Optional[datetime] = None) -> Optional[datetime]:
        """
        Attempt to parse a deadline from text given an optional reference time (defaults to now).
        """
        if not text:
            return None
        if reference_time is None:
            reference_time = datetime.now(timezone.utc)

        text_lower = text.lower()

        # 1. Check relative terms: "today", "tomorrow", "day after tomorrow"
        if "day after tomorrow" in text_lower:
            return reference_time + timedelta(days=2)
        if "tomorrow" in text_lower:
            target = reference_time + timedelta(days=1)
            # Check for specific time like "5 pm" or "17:00"
            hour, minute = cls._extract_time(text_lower)
            return target.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if "today" in text_lower:
            hour, minute = cls._extract_time(text_lower)
            return reference_time.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # 2. Check for "by Friday", "this Friday", "next Monday"
        weekday_match = re.search(r'\b(?:by|this|next|on)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text_lower)
        if weekday_match:
            target_weekday = cls.WEEKDAYS[weekday_match.group(1)]
            current_weekday = reference_time.weekday()
            days_ahead = (target_weekday - current_weekday) % 7
            if days_ahead == 0:
                days_ahead = 7
            target = reference_time + timedelta(days=days_ahead)
            hour, minute = cls._extract_time(text_lower)
            return target.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # 3. Check for explicit date: "October 24", "Oct 24, 2026", "24th Oct"
        month_pattern = r'\b(' + '|'.join(cls.MONTHS.keys()) + r')\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s*,\s*(\d{4}))?\b'
        match = re.search(month_pattern, text_lower)
        if match:
            month_str, day_str, year_str = match.groups()
            month = cls.MONTHS[month_str]
            day = int(day_str)
            year = int(year_str) if year_str else reference_time.year
            hour, minute = cls._extract_time(text_lower)
            try:
                return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
            except ValueError:
                pass

        # 4. Check ISO / slash dates: "2026-10-15" or "10/15/2026"
        iso_match = re.search(r'\b(\d{4})-(\d{2})-(\d{2})\b', text)
        if iso_match:
            try:
                y, m, d = map(int, iso_match.groups())
                return datetime(y, m, d, 17, 0, tzinfo=timezone.utc)
            except ValueError:
                pass

        return None

    @classmethod
    def _extract_time(cls, text: str) -> Tuple[int, int]:
        """
        Extract time of day (defaults to 17:00 / 5 PM if unspecified).
        """
        time_match = re.search(r'\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b', text)
        if time_match:
            h = int(time_match.group(1))
            m = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            if period == "pm" and h < 12:
                h += 12
            elif period == "am" and h == 12:
                h = 0
            return h, m
        return 17, 0  # Default 5:00 PM close of business


temporal_parser = TemporalParser()
