from __future__ import annotations

from babel.dates import parse_pattern, parse_date, parse_time
from datetime import timedelta, timezone, time, date, datetime, tzinfo
# timezone is a concrete implentation of abstract tzinfo class
from dateutil.tz import tzlocal
# from pytz import timezone
from typing import Optional, Final, Union
import re
from zoneinfo import ZoneInfo
from tzlocal import get_localzone_name

def debug(d1:object, d2:object=None) -> str:
    if isinstance(d1, datetime):
        s1 = f"Expected: {d1} and time {date_get_time(d1)} and tzinfo: {d1.tzinfo}"
    else:
        s1 = f"Expected: {d1}"
    if d2 is not None:
        if isinstance(d2, datetime):
            s2 = f"GOT: {d2} and time {date_get_time(d2)} and tzinfo: {d2.tzinfo}"
        else:
            s2 = f"GOT: {d2}"
    else:
        s2 = "None"

    return f"Assert failed; \n {s1} \n {s2}"

  
def date_get_time(dt:datetime) -> float:
    """ 
    Python wrapper for Java's ``Date.getTime()`` function.
    Returns the number of milliseconds since January 1, 1970, 00:00:00 GMT 
    represented by this ``datetime`` object.

    **Note**
    Java's validator calculates the time since the epoch using a ``Date`` object. 
    However, Java's ``Date`` is in the processes of deprecating all references to time fields (e.g. hour, minute, second, etc.).  
    In this project, even though we substitute python's ``date`` for Java's ``Date``,
    we will use Python's ``date`` does not store time fields, hence we will be using a ``datetime`` for this.

    Args: 
        dt (datetime): The Python date to get thet time from.
    
    Returns: 
        The number of milliseconds since January 1, 1970, 00:00:00 GMT represented by dt.
    """
    return dt.timestamp() * 1000

def timezone_gmt(zone:str) -> ZoneInfo:
    """
    Creates and returns a ``tzinfo`` object with the specified timezone.
    A replacement for Java's ``org.apache.commons.lang3.time.TimeZones``.

    Args:
        zone (str): The timezone to return. e.g. "est", or "gmt".
    
    Returns:
        A ``ZoneInfo`` object with the specified zone.
        Note that ``tzinfo`` is an abstract class, and ``ZoneInfo`` is an implementation.  
    """
    try:
        return ZoneInfo(zone)
    except Exception as e:
        print(f"Error, unable to create a tzinfo object with the specified zone, {zone}.")
        print(f"Error message: {e}")

def timezone_has_same_rules(val1: Union[datetime, tzinfo], val2: Union[datetime, tzinfo]) -> bool:
    """
    Wrapper function for java.util.TimeZone.hasSameRules().
    
    Determines if two datetime or tzinfo objects share the same rules for time adjustments,
    including the raw UTC offset and daylight saving time rules. This function disregards the
    time zone identifier (i.e. the name) and focuses solely on the effective behavior (offset)
    of the time zones.
    
    Args:
        val1 (Union[datetime, tzinfo]): A datetime object (from which the tzinfo is extracted)
            or a tzinfo instance representing the first time zone.
        val2 (Union[datetime, tzinfo, None]): A datetime object or tzinfo instance representing the
            second time zone. If None, the function returns False.
    
    Returns:
        ``True`` if the time zones have identical rules (i.e. the same UTC offset at the reference time); 
        ``False`` otherwise, or if either value does not have tzinfo information.
    """
    if val2 is None:
        return False

    # Extract tzinfo from datetime objects; if needed.
    tz1 = val1.tzinfo if isinstance(val1, datetime) else val1
    tz2 = val2.tzinfo if isinstance(val2, datetime) else val2

    if tz1 is None or tz2 is None:
        return False

    # Use a reference datetime for comparison.
    ref = datetime.now()
    offset1 = tz1.utcoffset(ref)
    offset2 = tz2.utcoffset(ref)

    return offset1 == offset2

def fmtt_java2py(java_input:str) -> str:
    return parse_pattern(java_input).format

def fmt_java2py(java_input:str) -> str:
    """
    Convert a Java SimpleDateFormat pattern into an equivalent Python strftime pattern.

    Steps:
        1. Scan the input string for substrings like 'yyyy', 'MM', 'dd', etc.
        2. For each match, look up its replacement in JAVA_TO_PY.
        3. Produce a new format string with all tokens swapped out.

    Example:
        java_fmt = "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
        returns "%Y-%m-%dT%H:%M:%S.%f%z"
    
    (Used for testing date, time, and calendar validators.)

    Args:
        java_fmt (str): The Java SimpleDateFormat pattern to convert
    
    Returns:
        The Python string pattern, that when fed into ``datetime.strftime()`` produces
        an equivalent date/time string representation.
    """
    # Define Java→Python token mappings.
    java2py = {
        'yyyy': '%Y',
        'yy':   '%y',
        'MMMM': '%B',
        'MMM':  '%b',
        'MM':   '%m',
        'M':    '%m',
        'dd':   '%d',
        'd':    '%d',
        'EEEE': '%A',
        'EEE':  '%a',
        'HH':   '%H',
        'H':    '%H',
        'hh':   '%I',
        'h':    '%I',
        'mm':   '%M',
        'm':    '%M',
        'ss':   '%S',
        's':    '%S',
        'SSS':  '%f',   # Java ms → Python μs; we'll truncate later if needed
        'a':    '%p',
        'z':    '%Z',     # General timezone (e.g. PST)
        'Z':    '%z',   # RFC 822 time zone (e.g. -0800)
        'XXX':  '%:z',  # Python 3.7+ supports “+HH:MM”
        'XX':   '%z',
        'X':    '%z',
    }

    # Build a regex that matches any of the Java tokens.
    combined = '|'.join(re.escape(tok) for tok in sorted(java2py, key=len, reverse=True))
    pattern = re.compile(combined)

    def replace(match):
        java_token = match.group(0)
        return java2py[java_token]

    # Every time the regex finds a Java token, it calls replace() to get the Python equivalent.
    return pattern.sub(repl=replace, string=java_input)

# def dt_format(dt:Union[datetime,date,time], pattern:str) -> str:
#     return dt.strftime(pattern)

class J2PyLocale:
    US:str = "en_US"
    GERMAN:str = "de"
    GERMANY:str = "de_DE"
    UK:str = "en_GB"


# Format a change a datetime to the timezone
def update_tz(dt:datetime, tz:tzinfo) -> datetime:
    print(f"TZ update: {dt}, has TZ: {dt.tzinfo}")
    if dt.tzinfo is None:
        ans = dt.replace(tzinfo=tz)
        print(f"TZ NONE: {ans}, has TZ: {ans.tzinfo}")

        # return dt.replace(tzinfo=tz)
    else:
        ans = dt.astimezone(tz=tz)
        print(f"TZ SOME: {ans}, has TZ: {ans.tzinfo}")
    return ans
        # return dt.astimezone(tz=tz)

locale_reg2dp_dict = {
    'en_US' : 'en-001',
    # 'en_US' : 'en-US',
    'en-GB' : 'en-150'
}
def locale_reg2dp(locale:str) -> str:
    """
    Coverts a locale string to the equivalent that `dateparser.parse()` will accept for it's `locales:list[str]` argument.
    Returns the original locale if a conversion is not found.
    """
    return locale_reg2dp_dict.get(locale, locale)


def get_default_tzinfo() -> tzinfo:
    """ 
    Gets the system's default timezone.
    """
    zone_name = get_localzone_name()
    tz_local = ZoneInfo(zone_name)
    return tz_local
    # return datetime.now().astimezone().tzinfo

def val_is_naive(val:str) -> bool:

    """Return True if dateutil finds a tzinfo in s."""
    from dateutil import parser
    try:
        dt = parser.parse(val, default=None)  # may raise if totally unparsable
        if dt.tzinfo == None:
            print(f"HELPER: val is naive: {val}")
            return True
        print(f"HELPER: val is aware: {val} with tzinfo {dt.tzinfo}")
        # return dt.tzinfo is None
        return False
    except Exception as e:
        print(f"HELPER: can't parse val: {val} with err message; {e}")
        return False

def get_tzname(tz:tzinfo):
    dt:datetime = datetime.now().astimezone(tz=tz)
    return dt.tzname()


def babel_parse_date(value, locale, pattern, time_zone) -> datetime:
    try:
        some_date = parse_date(string=value, locale=locale)
        none_time = time(0, 0, 0)
        dt = datetime.combine(some_date, none_time, tzinfo = time_zone)
        if dt is None:
            raise Exception
    except Exception as e:
        print(f"Babel_helper parse couldn't parse this this string. \n Message: {e}")
        return None
    return dt

def babel_parse_time(value, locale, pattern, time_zone) -> datetime:
    try:
        epoch_date = date(1970, 1, 1)
        some_time = parse_time(value, locale)
        dt = datetime.combine(epoch_date, some_time, tzinfo = time_zone)
        if dt is None:
            raise Exception
    except Exception as e:
        print(f"Babel_helper parse couldn't parse this this string. \n Message: {e}")
        return None
    return dt

zero_str = {
    ""
}

def babel_parse_datetime(value, locale, pattern, time_zone) -> datetime:
    try:
        date = parse_date(string=value, locale=locale)
        time = parse_time(string=value, locale=locale)
        dt = datetime.combine(date, time, tzinfo = time_zone)
        if dt is None:
            raise Exception
    except Exception as e:
        print(f"Babel_helper parse couldn't parse this this string. \n Message: {e}")
        return None
    return dt

def ldml2strptime(style_format:str = 'short', locale:str = None):
    """
    Gets the pattern to use in ``datetime.strptime()`` based on the input locale.
    """
    from babel.dates import get_time_format
    if locale is None:
        pattern = str(get_time_format(format=style_format))
    else:
        pattern = str(get_time_format(style_format, locale=locale))
    
    output = fmt_java2py(pattern)
    print(f"LDML mapped {pattern} to {output}")
    return output
    LDML_TO_STRPTIME = [
        (r"yyyy", "%Y"),
        (r"yy",   "%y"),
        (r"MM",   "%m"),
        (r"dd",   "%d"),
        (r"HH",   "%H"),
        (r"hh",   "%I"),
        (r"mm",   "%M"),
        (r"ss",   "%S"),
        (r"\ba\b", "%p"),           # careful: match 'a' token not in words
        # ... add more rules as needed
    ]
#  Attributes:
            # YEAR (int): The year.
            # MONTH (int): The month.
            #     The first month of the year (JANUARY) has a value of 0.
            # WEEK_OF_YEAR (int): the week number within the current year. 
            #     The first week of the year has value 1.
            # WEEK_OF_MONTH (int): The week number within the current month. 
            #     The first week of the month has value 1.
            # DATE (int): The day of the month. This is a synonym for DAY_OF_MONTH. 
            #     The first day of the month has value 1.
            # DAY_OF_YEAR (int): The day number within the current year. 
            #     The first day of the year has value 1. 
            # DAY_OF_WEEK (int): Day of the week. 
            #     In range 1 - 7, where 1 = SUNDAY and 7 = SATURDAY.
            # DAY_OF_WEEK_IN_MONTH (int): Corresponds to the ordinal number of the day of the week within the month.
            #     DAY_OF_MONTH 1-7 always corresponds to 1 for all weekdays (first occurence) 
            #     DAY_OF_MONTH 8-14 always corresponds to 2 for all weekdays (second occurence)
            # HOUR (int): The hour of the morning or afternoon. 
            #     HOUR is used for the 12-hour clock (0 - 11). 
            #     Noon and midnight are represented by 0, not by 12. 
            #     E.g., at 10:04:15.250 PM the HOUR is 10.
            # HOUR_OF_DAY (int): The hour of the day; used for the 24-hour clock. 
            #     E.g., at 10:04:15.250 PM the HOUR_OF_DAY is 22.
            # MINUTE (int): The minute within the hour. 
            #     E.g., at 10:04:15.250 PM the MINUTE is 4.
            # SECOND (int): = The second within the minute. 
            #     E.g., at 10:04:15.250 PM the SECOND is 15.
            # MILLISECOND (int): The millisecond within the second. 
            #     E.g., at 10:04:15.250 PM the MILLISECOND is 250.
#         """

#         int_to_field = {
#             1: "year",
#             2: "month",
#             3: "week_of_year",
#             4: "week_of_month",
#             5: "date",
#             6: "day_of_year",
#             7: "day_of_week",
#             8: "day_of_week_in_month",
#             10: "hour",
#             11: "hour_of_day",
#             12: "minute",
#             13: "second",
#             14: "millisecond",
#         }

#         datetime_fields = [
#             "year", 
#             "month", 
#             "day", 
#             "hour", 
#             "minute", 
#             "second", 
#             "microsecond", 
#             "tzinfo", 
#             "hashcode", 
#             "fold"
#         ]

#     # Partial mapping of Java.util.Calendar fields to python's calendar constants
#     def __init__(self):
#         """Creates a Calendar object and initializes all fields to None."""
#         self._time:datetime = None
#         self.fields = {field:None for field in CalendarWrapper.Field}

#    # datetime.replace()
#     # def set(self, field:Union[Field, int], value: int):
#     #     """Sets the specified field to the given value. May recompute other fields."""
#     #     if isinstance(field, self.Field):
#     #         field_name = field.name
#     #         field_value = field.value
#     #     else:
#     #         field_name = next((f.name for f in self.Field if f.value == field), str(field))
#     #         field_value = field
        
#     #     if field_value in self.fields:
#     #         self.fields[field_value] = value
#     #     else:
#     #         raise ValueError(f"Invalid field: {field_name}")
    
#    # datetime.day # example field accesss
#     # def get(self, field:Union[Field, int]) -> int:
#     #     """ 
#     #     Gets the specified field.

#     #     Args:
#     #         field (Union[Calendar.Field, int]): The field to retrieve.

#     #     Returns
#     #         The value of the specified field.

#     #     Raises:
#     #         ValueError if the field is invalid
#     #     """
#     #     if isinstance(field, self.Field):
#     #         field_name = field.name
#     #         field_value = field.value
#     #     else:
#     #         field_name = next((f.name for f in self.Field if f.value == field), str(field))
#     #         field_value = field
        
#     #     if field_value in self.fields:
#     #         return self.fields[field_value]
#     #     else:
#     #         raise ValueError(f"Invalid field: {field_name}")
    

#     def get_instance(self, zone:Optional[timezone], a_locale:Locale) -> datetime:
#         """
#         Gets a calendar using the default time zone and locale. 
#         The Calendar returned is based on the current time in the default time zone with the default `FORMAT` locale.
        
#         Args:
#             zone (TimeZone): The time zone to use.
#             a_locale (Locale): The locale for the week data.

#         Returns:
#             a Calendar.
#         """
#         # Get the current datetime object.
#         if zone is None:
#             # for local timezone, use `tzlocal()`
#             # for utc timezone, use `timezone.utc`
#             now = datetime.now(tz = tzlocal())
#         else:
#             # Or use passed in timezone
#             now = datetime.now(tz = zone)

#         new_calendar = Calendar()

#         # Set the current time
#         new_calendar._time = now
        
#         # populate calendar fields
#         new_calendar.set(Calendar.Field.YEAR, now.year)
#         # now.month is 1 indexed, but Java's MONTH is zero-indexed.
#         new_calendar.set(Calendar.Field.MONTH, now.month - 1)
#         new_calendar.set(Calendar.Field.WEEK_OF_YEAR, now.isocalendar()[1])
#         # new_calendar.set(Calendar.Field.WEEK_OF_MONTH, ((now.day // 7) + 1))
#         new_calendar.set(Calendar.Field.WEEK_OF_MONTH, self._week_of_month(now))
#         new_calendar.set(Calendar.Field.DATE, now.day)
#         new_calendar.set(Calendar.Field.DAY_OF_YEAR, now.timetuple().tm_yday)
#         # Python's now.isoweeday() assigns 1 as Monday, and 7 as Sunday. 
#         # Java's Calendar implementation, assigns 1 as Sunday and 7 as Saturday.
#         new_calendar.set(Calendar.Field.DAY_OF_WEEK, (now.isoweekday() + 1)%7)
#         new_calendar.set(Calendar.Field.DAY_OF_WEEK_IN_MONTH, self._day_of_week_in_month(now))
#         new_calendar.set(Calendar.Field.HOUR, now.hour % 12)
#         new_calendar.set(Calendar.Field.HOUR_OF_DAY, now.hour)
#         new_calendar.set(Calendar.Field.MINUTE, now.minute)
#         new_calendar.set(Calendar.Field.SECOND, now.second)
#         new_calendar.set(Calendar.Field.MILLISECOND, (now.microsecond) // 1000)
        


# def get_time(value:datetime) -> date:
#     """
#     Returns a ``date`` object representing this datetime's time value (millisecond offset from the Epoch).

#     **Note**:
#         The "Epoch" refers to January 1, 1970 00:00:00.000 GMT (Gregorian).
    
#     Returns:
#         A ``date`` created from value's fields.
#     """
#     return value.date()

# def get_time_zone(value:datetime) -> tzinfo:
#     """
#     Gets the timezone of the datetime. ``None``, if value is a naive datetime object.
#     """
#     return value.tzinfo

# class DateFormatter:
#     """
#     Wrapper class to format dates and times according to the timezone.
#     Enforces singleton behavrior, ensuring thread safety.

#     Attributes:
#         locale (str): The locale of the date and time to format to. 
#             Uses the system's default if not set
#         date_formatter (DateFormatter): A singleton instance of this class
#     """
#     __locale:str = Locale.getdefaultlocale()
#     __timezone:str = None
#     __date_formatter:DateFormatter = None
        
#     @classmethod
#     @property
#     def date_formatter(cls):
#         """
#         Enforces singleton behavior and returns the singleton instance of this class.

#         Returns:
#             A singleton instance of the ``DateFormatter``.
#         """
#         if cls.__date_formatter is None:
#             cls.__date_formatter = DateFormatter()
#         return cls.__date_formatter
    
#     def _format_date(value:date) -> str:
#         """
#         Calls ``datetime.strftime()`` on a ``date`` to format the date as a string.

#         Args: 
#             value (date): The ``date`` to format as a string.
        
#         Returns: 
#             The value formatted as a string.
#         """
#         pass
    
#     def _format_time(value:time) -> str:
#         """
#         Calls ``datetime.strftime()`` on a ``time`` to format the time as a string.

#         Args: 
#             value (time): The ``time`` to format as a string.
        
#         Returns: 
#             The value formatted as a string.
#         """
#         pass
    
#     def _format_datetime(value:datetime) -> str:
#         """
#         Calls ``datetime.strftime()`` on a ``datetime`` to format the time as a string.

#         Args: 
#             value (time): The ``datetime`` to format as a string.
        
#         Returns: 
#             The value formatted as a string.
#         """
#         pass
    

#     def format_obj(value:object, ) -> str:
#         """
#         Formats a date 
#         """
    


# # ---- Helper functions to calculate missing fields: ----
# def _week_of_month(dt: datetime) -> int:
#     """
#     Calculates the week of the month for a given date, similar to Java's Calendar.WEEK_OF_MONTH.
    
#     The calculation uses Sunday as the first day of the week (Java's default).
#     It returns the week number (1-based) in which the given day occurs.
    
#     Args:
#         dt (datetime): The date for which to calculate the week of the month.
    
#     Returns:
#         int: The week of the month (1-based). For example, if dt is in the first week, it returns 1.
#     """
#     # Create a Calendar with Sunday as the first day of the week.
#     cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
#     # monthdayscalendar returns a list of weeks; each week is a list of 7 integers.
#     # Days outside the current month are represented by 0.
#     month_weeks = cal.monthdayscalendar(dt.year, dt.month)
    
#     # Loop through the weeks to see which one contains the day.
#     for week_index, week in enumerate(month_weeks, start=1):
#         if dt.day in week:
#             return week_index
#     # Fallback (should not occur if dt is valid)
#     return 0


# def _day_of_week_in_month(date:datetime):
#     """
#     Calculate the ordinal number of the day of the week within the current month.
    
#     Args:
#         date (datetime): The date for which to calculate the day of week in month.
        
#     Returns:
#         int: The ordinal number of the day of the week in the month.
#     """
#     # Find the first occurrence of the day of the week in the month
#     first_day_of_month = date.replace(day=1)
#     first_occurrence = first_day_of_month.weekday()  # Monday is 0, Sunday is 6
    
#     # Calculate the day of the month
#     day_of_month = date.day
    
#     # Determine the ordinal number
#     ordinal = (day_of_month + first_occurrence) // 7 + 1

#     return ordinal