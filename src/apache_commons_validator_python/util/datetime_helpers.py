"""
Module Name: datetime_helpers.py

Description:
    Helper functions and constants for date/time parsing and validation.

This module provides:
- Mappings from Java date/time locales and patterns to Python equivalents.
- Utilities for obtaining system default locale and timezone information.
- Conversion between Java SimpleDateFormat patterns (LDML) and Python strptime formats.
- Wrappers around `dateparser` for flexible and strict parsing.
- Comparison of timezone behaviors analogous to Java's `TimeZone.hasSameRules()`.

Classes:
    JavaToPyLocale
        Constants for common Java locale identifiers.

Functions:
    obj_to_str
    get_default_locale
    get_default_tzinfo
    get_tzname
    date_get_time
    timezone_gmt
    timezone_has_same_rules
    ldml_to_strptime_format
    fuzzy_parse
    ldml2strptime
    ldml2strpdate
    parse_pattern_strict
    parse_pattern_flexible

Author:
    Juji Lau
"""
from babel.dates import (
    parse_pattern, 
    get_date_format, 
    get_time_format
)
from dateparser import parse
from datetime import date, datetime, tzinfo
import locale
import re
from typing import Union
from tzlocal import get_localzone_name
from zoneinfo import ZoneInfo


# ----------------------------- Constants -------------------------------:
class JavaToPyLocale:
    """
    Wrapper constants to convert Java locale identifiers to Python locale strings.

    Attributes:
        US (str): English (United States).
        GERMAN (str): German (general).
        GERMANY (str): German (Germany).
        UK (str): English (United Kingdom).
    """
    US:str = "en_US"
    GERMAN:str = "de"
    GERMANY:str = "de_DE"
    UK:str = "en_GB"

# Mapping from Java locale strings to locale strings accepted by dateparser.parse()
locale_to_dateparser_locale = {
    'en_US' : 'en-001',
    'en-GB' : 'en-150'
}


# ----------------------------- Helper Functions -------------------------------:

# --------------- Utility Functions ---------------:
def obj_to_str(expected_obj:object, tested_obj:object=None) -> str:
    """
    Generate a comparison string for expected and tested objects (for debugging).

    Args:
        expected_obj (object): The expected test result (datetime or other).
        tested_obj (object, optional): The actual test result to compare. Defaults to None.

    Returns:
        str: Detailed comparison of expected vs. actual, including time since the unix epoch and tzinfo for datetimes.
    """
    if isinstance(expected_obj, datetime):
        str_expect = f"Expected: {expected_obj} and time {date_get_time(expected_obj)} and tzinfo: {expected_obj.tzinfo}"
    else:
        str_expect = f"Expected: {expected_obj}"
    if tested_obj is not None:
        if isinstance(tested_obj, datetime):
            str_test = f"GOT: {tested_obj} and time {date_get_time(tested_obj)} and tzinfo: {tested_obj.tzinfo}"
        else:
            str_test = f"GOT: {tested_obj}"
    else:
        str_test = "None"

    return f"Assert failed; \n {str_expect} \n {str_test}"


def get_default_locale() -> str:
    """
    Retrieve the system's default locale code.

    Returns:
        str: Locale code (e.g., 'en_US').
    """
    loc = locale.getlocale()
    return loc[0]



def get_default_tzinfo() -> tzinfo:
    """
    Retrieve the system's default timezone as a tzinfo object.

    Returns:
        tzinfo: System local timezone.
    """
    zone_name = get_localzone_name()
    tz_local = ZoneInfo(zone_name)
    return tz_local


def get_tzname(timezone:tzinfo) -> str:
    """
    Get the name of a tzinfo object.

    Note:
        Functionally the same as ``datetime.tzname``, except `tzinfo` does not have a ``name`` field.
   
    Args:
        timezone (tzinfo): tzinfo instance to get the name of.

    Returns:
        str: tzinfo object's name (e.g., 'PST').
    """
    dt:datetime = datetime.now().astimezone(tz=timezone)
    return dt.tzname()

  
def date_get_time(dt:datetime) -> float:
    """
    Return milliseconds since Unix epoch (January 1, 1970, 00:00:00 GMT) for a datetime.
    
    Python wrapper for Java's ``Date.getTime()`` function.
    
    Args:
        dt (datetime): Input datetime.

    Returns:
        float: Milliseconds since 1970-01-01T00:00:00Z.
    """
    return dt.timestamp() * 1000


def timezone_gmt(zone:str) -> ZoneInfo:
    """
    Create a tzinfo object for a given timezone name.

    Wrapper for Java's ``org.apache.commons.lang3.time.TimeZones``.


    Args:
        zone (str): Timezone identifier (e.g., 'UTC', 'America/New_York').

    Returns:
        tzinfo or None: ZoneInfo instance or None if invalid.
    """
    try:
        return ZoneInfo(zone)
    except Exception as e:
        print(f"Error, unable to create a tzinfo object with the specified zone, {zone}.")
        print(f"Error message: {e}")


def timezone_has_same_rules(val1: Union[datetime, tzinfo], val2: Union[datetime, tzinfo]) -> bool:
    """
    Determine if two timezones share the same UTC offset and DST time adjustment rules,
    including the raw UTC offset and daylight saving time rules. Disregards the
    time zone identifier (i.e. the name) and focuses solely on the effective behavior 
    (time zone offset).

    Wrapper function for java.util.TimeZone.hasSameRules().

    Args:
        val1 (Union[datetime, tzinfo]): First datetime or tzinfo.
        val2 (Union[datetime, tzinfo]): Second datetime or tzinfo.

    Returns:
        bool: True if both have identical offset rules; False if otherwise or if 
        `val1` or `val2` is None.
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



# ------------ Parsing Functions ---------------:
def ldml_to_strptime_format(java_input:str) -> str:
    """
    Convert Java SimpleDateFormat patterns to patterns accepted by Python's ``strptime()``.

    Args:
        java_fmt (str): Java date/time format string (ldml format).

    Returns:
        str: Equivalent Python strftime format.
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


def fuzzy_parse(*, value:str, pattern:str, locale:str, settings:dict) -> datetime:
    """
    Attempt to parse a datetime string using `dateparser.parse()`, respecting locale and pattern
    with fallback strategies for language-only or region-only parsing.

    Note:
        This function is a last resort, only called if all else fails, because 
        ``dateparser.parse()`` is too loose; it allows differing value strings to be parsed. 
        It exists ``dateparser.parse()`` is best for parsing locale sensitive strings.
    
    Args:
        value (str): Date/time string to parse.
        pattern (str): LDML pattern for parsing.
        locale (str): Locale code (e.g., 'en_US').
        settings (dict): Additional settings for dateparser.

    Returns:
        datetime or None: Parsed datetime or None if all attempts fail.
    """
    date_parser_locale = locale_to_dateparser_locale.get(locale, locale)
    dt = parse(date_string=value, date_formats=[pattern], locales=[date_parser_locale], settings=settings)
    if dt is None:
        if "_" in locale:
            lang, country = locale.split("_")
            dt = parse(value, date_formats = [pattern], languages = [lang], settings=settings)
            if dt is None:
                dt = parse(value, date_formats = [pattern], region=country, settings=settings)
        else:
            # Try language only
            dt = parse(value, languages = [date_parser_locale], settings=settings)
            if dt is None:
                # Try country only
                dt = parse(value, region = date_parser_locale, settings=settings)
    return dt


def ldml2strptime(value:str, style_format:str = 'short', locale:str = None) -> datetime:
    """
    Parse a time string into datetime using Babel's LDML style formats.

    Args:
        value (str): `time` string to parse.
        style_format (str): LDML style ('short', 'medium', 'long', 'full').
        locale (str, optional): Locale code to use; system default if None.
    
    Returns:
        datetime or None: Parsed datetime or None on parsing failure.
    """   
    # Get the default locale if locale is None
    if locale is None:
        locale = get_default_locale()
    
    try:
        # Strict parsing using strptime()
        ldml_pattern = get_time_format(format=style_format, locale=locale).pattern
        return parse_pattern_strict(value, ldml_pattern)
    
    except Exception as e:
        return None


def ldml2strpdate(value:str, style_format:str = 'short', locale:str = None) -> datetime:
    """
    Parse a date string into datetime using Babel's LDML style formats.

    Args:
        value (str): `date` string to parse.
        style_format (str): LDML style ('short', 'medium', 'long', 'full').
        locale (str, optional): Locale code to use; system default if None.
    
    Returns:
        datetime or None: Parsed datetime or None on parsing failure.
    """ 
    # Get the default locale if locale is None
    if locale is None:
        locale = get_default_locale()

    try:
        ldml_pattern = get_date_format(format=style_format, locale=locale).pattern
        if style_format == 'short':
            # Flexible parsing using regex
            return parse_pattern_flexible(value, ldml_pattern)
        else:
            # Strict parsing using strptime()
            return parse_pattern_strict(value, ldml_pattern)

    except Exception as e:
        return None


def parse_pattern_strict(value:str, ldml_pattern:str) -> datetime:
    """
    Strictly parse a string into datetime using a converted LDML pattern.

    Args:
        value (str): String to parse.
        ldml_pattern (str): LDML pattern to convert and use.

    Returns:
        datetime: Parsed datetime.
    """
    pat = ldml_to_strptime_format(ldml_pattern)
    return datetime.strptime(value, pat)


def parse_pattern_flexible(value:str, ldml_pattern:str) -> datetime:
    """
    Flexibly parse a date string mimicking Java's flexible locale-dependent 'short' style.

    There are multiple acceptable "short" strings per locale in Java's SimpleDateFormat, 
    but only one acceptable "short" string per locale in Python. 
    
    Args:
        value (str): Date string to parse.
        ldml_pattern (str): LDML 'short' pattern to guide parsing.

    Returns:
        datetime or None: Parsed datetime or None if unparseable.
    """
    pat = parse_pattern(ldml_pattern).format  # e.g. '%(M)s/%(d)s/%(yy)s'

    # 2. Build regex from tokens
    token_re = re.compile(r'%\((?P<tok>.*?)\)s')
    parts = []
    last = 0
    for m in token_re.finditer(pat):
        # literal part
        lit = re.escape(pat[last:m.start()])
        parts.append(lit)
        # token part
        tok = m.group('tok')
        if tok.startswith('d'):        # d, dd, ddd… → day
            parts.append(r'(?P<day>\d+)')
        elif tok.startswith('M'):      # M, MM, MMM… → month
            parts.append(r'(?P<month>\d+)')
        elif tok.startswith('y'):      # y, yy, yyyy… → year
            parts.append(r'(?P<year>\d+)')
        else:
            raise ValueError(f"Unsupported token: {tok}")
        last = m.end()
    parts.append(re.escape(pat[last:]))
    regex = '^' + ''.join(parts) + '$'

    # 3. Match and extract
    m = re.match(regex, value)
    if not m:
        print(f"Unparseable date: {value!r} for pattern {ldml_pattern!r}")
        return None

    # 4. Convert fields
    month = int(m.group('month'))
    day   = int(m.group('day'))
    ystr  = m.group('year')
    # Pivot two‐digit years
    if len(ystr) == 2 and ystr.isdigit():
        now = date.today()
        pivot = now.year - 80
        century = pivot - (pivot % 100)
        year = century + int(ystr)
        if year < pivot:
            year += 100
    else:
        year = int(ystr)

    return datetime(year, month, day)