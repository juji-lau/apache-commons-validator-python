from __future__ import annotations

from babel.dates import parse_pattern, get_date_format, get_time_format
from datetime import date, datetime, tzinfo
from typing import Union
import re
from zoneinfo import ZoneInfo
from tzlocal import get_localzone_name
import locale

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


class J2PyLocale:
    US:str = "en_US"
    GERMAN:str = "de"
    GERMANY:str = "de_DE"
    UK:str = "en_GB"


locale_reg2dp_dict = {
    'en_US' : 'en-001',
    'en-GB' : 'en-150'
}
def locale_reg2dp(locale:str) -> str:
    """
    Coverts a locale string to the equivalent that `dateparser.parse()` will accept for it's `locales:list[str]` argument.
    Returns the original locale if a conversion is not found.
    """
    return locale_reg2dp_dict.get(locale, locale)

def get_default_locale() -> str:
    """
    Gets the system's default locale (`en_US`).
    """
    loc = locale.getlocale()
    return loc[0]


def get_default_tzinfo() -> tzinfo:
    """ 
    Gets the system's default timezone.
    """
    zone_name = get_localzone_name()
    tz_local = ZoneInfo(zone_name)
    return tz_local


def get_tzname(tz:tzinfo):
    dt:datetime = datetime.now().astimezone(tz=tz)
    return dt.tzname()


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
    """
    Parses the value to a ``datetime`` based on the style_format and locale.
    Uses system default if the locale is ``None``.

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
    pat = fmt_java2py(ldml_pattern)
    return datetime.strptime(value, pat)


def parse_pattern_flexible(value:str, ldml_pattern:str) -> datetime:
    """
    Parses value string into the representing datetime in the locale's "short" style.
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