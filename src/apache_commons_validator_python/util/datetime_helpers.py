"""
TODO: insert module description
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
    """Wrapper class to convert Java's locales to a Python locale string."""
    US:str = "en_US"
    GERMAN:str = "de"
    GERMANY:str = "de_DE"
    UK:str = "en_GB"

# Parses a locale string to a form that `dateparser.parse()` accepts.
locale_to_dateparser_locale = {
    'en_US' : 'en-001',
    'en-GB' : 'en-150'
}


# ----------------------------- Helper Functions -------------------------------:

# --------------- Utility Functions ---------------:
def obj_to_str(expected_obj:object, tested_obj:object=None) -> str:
    """Prints the object as a string for debugging purposes on the test cases.

    Args:
        expected_obj (Union[datetime, object]): The expected object in the test case.
        tested_obj (Union[datetime, object]): The object being tested in the test case.

    Returns:
        A string comparing the expected_obj and tested_obj and their fields if applicable.
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
    """Gets the system's default locale (`en_US`)."""
    loc = locale.getlocale()
    return loc[0]



def get_default_tzinfo() -> tzinfo:
    """Gets the system's default timezone."""
    zone_name = get_localzone_name()
    tz_local = ZoneInfo(zone_name)
    return tz_local


def get_tzname(timezone:tzinfo) -> str:
    """
    Returns the name of the timezone (same as ``datetime.tzname``).
    `tzinfo` does not have a name field, so this function is nessescary to get the name of a lone tzinfo objct.

    Args:
        timezone (tzinfo): The tzinfo object that we want the name of

    Returns:
        The name of timezone as a string.  
    """
    dt:datetime = datetime.now().astimezone(tz=timezone)
    return dt.tzname()

  
def date_get_time(dt:datetime) -> float:
    """Python wrapper for Java's ``Date.getTime()`` function. Returns the number of
    milliseconds since January 1, 1970, 00:00:00 GMT represented by this ``datetime``
    object.

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
    """Creates and returns a ``tzinfo`` object with the specified timezone. A
    replacement for Java's ``org.apache.commons.lang3.time.TimeZones``.

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



# ------------ Parsing Functions ---------------:
def ldml_to_strptime_format(java_input:str) -> str:
    """Convert a Java SimpleDateFormat pattern into an equivalent Python strftime
    pattern.

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


def fuzzy_parse(*, value:str, pattern:str, locale:str, settings:dict) -> datetime:
    """
    Uses ``dateparser.parse()`` to parse a datetime given a value string, locale, and pattern.
    This is a last resort, if all else fails, because dateparser.parse() is too loose;
    it allows differing value strings to be parsed. We still use it because it respects locales the best.
    
    Args:
        TODO
    
    Returns: 
        TODO
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
    Parses the value to a ``datetime`` based on the style_format and locale.
    Uses system default if the locale is ``None``.

    Args:
        value (str): The string to parse into a ``datetime``
        style_format (str): The style of the ``value`` string passed in ('short' by default.) 
            One of: 'short', 'medium', 'long', or 'full'
        locale (str): The locale of the value string.
    
    Returns:
        The parsed ``datetime`` from the value string.
        ``None`` if the value string is unparseable with the given locale.
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
    """Parses the value to a ``datetime`` based on the style_format and locale. Uses
    system default if the locale is ``None``.

    Args:
        value (str): The string to parse into a datetie
        style_format (str): The style of the ``value`` string passed in ('short' by default.)
            One of: 'short', 'medium', 'long', or 'full'
        locale (str): The locale of the value string.

    Returns:
        The parsed ``datetime`` from the value string.
        ``None`` if the value string is unparseable with the given locale.
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
    TODO:
    """
    pat = ldml_to_strptime_format(ldml_pattern)
    return datetime.strptime(value, pat)


def parse_pattern_flexible(value:str, ldml_pattern:str) -> datetime:
    """
    TODO: Parses value string into the representing datetime in the locale's "short" style.
    Except there are multiple acceptable "short" strings in Java, but only one acceptable 
    "short" string in Python. This function aims to mimic Java's flexibility. Uses the 
    system's default locale if a locale is not provided.
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