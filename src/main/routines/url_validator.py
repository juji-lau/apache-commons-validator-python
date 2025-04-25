"""
Module Name: url_validator.py

Description: Translates apache.commons.validator.routines.UrlValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/UrlValidator.java

Author: Jessica Breuhaus

License (Taken from apache.commons.validator.routines.UrlValidator.java):
    Licensed to the Apache Software Foundation (ASF) under one or more
    contributor license agreements.  See the NOTICE file distributed with
    this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0
    (the "License"); you may not use this file except in compliance with
    the License.  You may obtain a copy of the License at

        http:#www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from typing import Final
import re
import urllib.parse
from ..routines.regex_validator import RegexValidator
from ..routines.domain_validator import DomainValidator
from ..routines.inet_address_validator import InetAddressValidator
# from ..generic_validator import GenericValidator

class UrlValidator:
    """
    URL Validation routines.
    Behavior of validation is modified by passing in options:
        <li>ALLOW_2_SLASHES - [FALSE]  Allows double '/' characters in the path component.</li>
        <li>NO_FRAGMENT - [FALSE]  By default fragments are allowed, if this option is included then fragments are flagged as illegal.</li>
        <li>ALLOW_ALL_SCHEMES - [FALSE] By default only http, https, and ftp are considered valid schemes. Enabling this option will let any scheme pass validation.</li>

    Originally based in on php script by Debbie Dyer, validation.php v1.2b, Date: 03/07/02,
    https://javascript.internet.com. However, this validation now bears little resemblance to the php original.

    Example of usage:
    Construct a UrlValidator with valid schemes of "http", and "https".
        schemes = {"http","https"}.
        url_validator = UrlValidator(schemes);
        if (url_validator.is_valid("ftp://foo.bar.com/")):
            print("URL is valid")
        else:
            print("URL is invalid")
    prints "URL is invalid"
    
    If instead the default constructor is used.
        url_validator = UrlValidator();
        if (url_validator.is_valid("ftp://foo.bar.com/")):
            print("URL is valid")
        else:
            print("URL is invalid")
    prints out "URL is valid"

    See "http://www.ietf.org/rfc/rfc2396.txt"
    Uniform Resource Identifiers (URI): Generic Syntax

    Attributes:
        <li>serializable (bool): Indicates if the object is serializable.</li>
        <li>cloneable (bool): Indicates if the object can be cloned.</li>
        <li>ALLOW_ALL_SCHEMES (int): Allow all validly formatted schemes to pass validation instead of supplying a set of valid schemes.</li>
        <li>ALLOW_2_SLASHES (int): Allow two slashes in the path component of the URL.</li>
        <li>NO_FRAGMENTS (int): Disallow any URL fragments.</li>
        <li>ALLOW_LOCAL_URLS (int): Allow local URLs, enabling a broad-brush check.</li>
    """
    serializable = True
    cloneable    = False

    __MAX_UNSIGNED_16_BIT_INT: Final[int] = 0xFFFF
    
    ALLOW_ALL_SCHEMES: Final[int] = 1 << 0
    """Allows all validly formatted schemes to pass validation instead of supplying a set of valid schemes."""

    ALLOW_2_SLASHES: Final[int] = 1 << 1
    """Allow two slashes in the path component of the URL."""

    NO_FRAGMENTS: Final[int] = 1 << 2
    """Enabling this options disallows any URL fragments."""

    ALLOW_LOCAL_URLS: Final[int] = 1 << 3
    """
    Allow local URLs, such as https://localhost/ or https://machine/ .
    This enables a broad-brush check, for complex local machine name
    validation requirements you should create your validator with
    RegexValidator instead UrlValidator(RegexValidator, int)
    """

    __SCHEME_REGEX: Final[str] = r"^[A-Za-z][A-Za-z0-9+\-\.]*"
    """Protocol scheme (for example, http, ftp, https)."""
    __SCHEME_PATTERN = re.compile(__SCHEME_REGEX)

    __AUTHORITY_REGEX = r"(?:\[((::FFFF:(?:\d{1,3}\.){3}\d{1,3})|([0-9a-fA-F:]+))\]|(?:(?:[a-zA-Z0-9%\-._~!$&'()*+,;=]+(?::[a-zA-Z0-9%\-._~!$&'()*+,;=]*)?@)?([A-Za-z0-9\-\.]*)))(?::(\d*))?(.*)?"
    __AUTHORITY_PATTERN = re.compile(__AUTHORITY_REGEX)

    __PARSE_AUTHORITY_IPV6: Final[int]    = 1
    __PARSE_AUTHORITY_HOST_IP: Final[int] = 4
    __PARSE_AUTHORITY_PORT: Final[int]    = 5
    __PARSE_AUTHORITY_EXTRA: Final[int]   = 6
    """Should always be empty. The code currently allows spaces."""

    __PATH_REGEX: Final[str] = r"^(/[-\w:@&?=+,.!/~*'%$_;\(\)]*)?$"
    __PATH_PATTERN = re.compile(__PATH_REGEX)

    __QUERY_REGEX: Final[str] = r"^(?:[^%]*|(?:%[0-9A-Fa-f]{2}))*$"
    __QUERY_PATTERN = re.compile(__QUERY_REGEX)

    __DEFAULT_SCHEMES: Final[list] = ["http", "https", "ftp"] # Must be lower-case
    """If no schemes are provided, default to this set."""

    __DEFAULT_URL_VALIDATOR = None
    """Singleton instance of this class with default schemes and options."""

    @classmethod
    def get_instance(cls):
        """
        Returns the singleton instance of this class with default schemes and options.
        :return: Singleton instance with default schemes and options.
        """
        if not cls.__DEFAULT_URL_VALIDATOR:
            cls.__DEFAULT_URL_VALIDATOR = UrlValidator()
        return cls.__DEFAULT_URL_VALIDATOR
    
    def __init__(self, schemes: list[str]=None, authority_validator: RegexValidator=None, options: int=0,
                 domain_validator: DomainValidator=None):
        """
        Constructs a new instance with the given validation options.

        :param schemes: The list of valid schemes. Ignored if the ALLOW_ALL_SCHEMES option is set.
        :param authority_validator: Regular expression validator used to validate the authority part.
        :param options: Validation options. Set using the public constants of this class.
        To set multiple options, simply add them together: ALLOW_2_SLASHES + NO_FRAGMENTS enables both of those options.
        :param domain_validator: The DomainValidator to use; must agree with ALLOW_LOCAL_URLS setting.
        """
        self.__options = options

        if not domain_validator:
            domain_validator = DomainValidator.get_instance(allow_local=self.__is_on(self.ALLOW_LOCAL_URLS, options))
        self.__domain_validator = domain_validator

        if domain_validator.allow_local != ((options & self.ALLOW_LOCAL_URLS) > 0):
            raise("DomainValidator disagrees with ALLOW_LOCAL_URLS setting")

        if self.__is_on(self.ALLOW_ALL_SCHEMES):
            self.__allowed_schemes = set()
        else:
            if not schemes:
                schemes = self.__DEFAULT_SCHEMES
            self.__allowed_schemes = set()
            for scheme in schemes:
                self.__allowed_schemes.add(scheme.lower())

        self.__authority_validator = authority_validator
    
    def _count_token(self, token: str, target: str):
        """
        Returns the number of times the token appears in the target.

        :param token: Token value to be counted.
        :param target: Target value to count tokens in.
        :return: The number of tokens.
        """
        return target.count(token)
    
    def __is_off(self, flag: int):
        """
        Tests whether the given flag is off.  If the flag is not a power of 2
        (for example, 3) this tests whether the combination of flags is off.

        :param flag: Flag value to check.
        :return: Whether the specified flag value is off.
        """
        return (self.__options & flag) == 0
    
    def __is_on(self, flag: int, options: int=None):
        """
        Tests whether the given flag is on.  If the flag is not a power of 2
        (for example, 3) this tests whether the combination of flags is on.

        :param flag: Flag value to check.
        :param options: What to check. If not given, will check this instances options.
        :return: Whether the specified flag value is on.
        """
        if options:
            return (options & flag) > 0
        return (self.__options & flag) > 0
    
    def is_valid(self, value: str):
        """
        Checks if a field has a valid URL address.</p>

        Note that the method calls is_valid_authority() which checks that the domain is valid.
    
        :param value: The value validation is being performed on. None is considered an invalid value.
        :return: True if the URL is valid.
        """
        if not value:
            return False
        
        # ensure value is a valid URI
        try:
            uri = urllib.parse.urlparse(value)
        except Exception:
            return False
        
        # now perform additional validation
        scheme = uri.scheme
        if not self._is_valid_scheme(scheme):
            return False
        
        authority = uri.netloc
        # if scheme == "file" and GenericValidator.is_blank_or_null(authority):
        if scheme == "file" and (not authority or authority == ''):
            return self._is_valid_path(uri.path)
        
        # validate the authority
        if (scheme == "file" and ':' in authority) or not self._is_valid_authority(authority):
            return False
        
        if not self._is_valid_path(uri.path) or not self._is_valid_query(uri.query) or not self._is_valid_fragment(uri.fragment):
            return False
        
        return True
        
    def _is_valid_authority(self, authority: str):
        """
        Returns true if the authority is properly formatted. An authority is the combination
        of hostname and port. An authority value of None is considered invalid.
        Note: this implementation validates the domain unless a RegexValidator was provided.
        If a RegexValidator was supplied, and it matches, then the authority is regarded
        as valid with no further checks, otherwise the method checks against the
        AUTHORITY_PATTERN and the DomainValidator (ALLOW_LOCAL_URLS)
        
        :param authority: Authority value to validate, allows IDN.
        :return: True if authority (hostname and port) is valid.
        """
        if not authority:
            return False
        
        # check manual authority validation if specified
        if self.__authority_validator and self.__authority_validator.is_valid(authority):
            return True
        
        # convert to ASCII if possible
        authority_ascii = DomainValidator.unicode_to_ascii(authority)

        authority_matches = self.__AUTHORITY_PATTERN.fullmatch(authority_ascii)
        if not authority_matches:
            return False

        # We have to process IPV6 separately because that is parsed in a different group
        ipv6 = authority_matches.group(self.__PARSE_AUTHORITY_IPV6)
        if ipv6:
            inet_address_validator = InetAddressValidator.get_instance()
            if not inet_address_validator.is_valid_inet6_address(ipv6):
                return False
        else:
            host_location = authority_matches.group(self.__PARSE_AUTHORITY_HOST_IP)
            # check if authority is hostname or IP address:
            # try a hostname first since that's much more likely
            if not self.__domain_validator.is_valid(host_location):
                # try an IPv4 address
                inet_address_validator = InetAddressValidator.get_instance()
                if not inet_address_validator.is_valid_inet4_address(host_location):
                    # isn't IPv4, so the URL is invalid
                    return False
            
            port = authority_matches.group(self.__PARSE_AUTHORITY_PORT)
            # if not GenericValidator.is_blank_or_null(port):
            if port:
                try:
                    i_port = int(port)
                    if i_port < 0 or i_port > self.__MAX_UNSIGNED_16_BIT_INT:
                        return False
                except ValueError:
                    return False # this can happen for big numbers
        
        extra = authority_matches.group(self.__PARSE_AUTHORITY_EXTRA)
        if extra and extra.strip() != '':
            return False
        
        return True
    
    def _is_valid_fragment(self, fragment: str):
        """
        Returns true if the given fragment is None or fragments are allowed.
        
        :param fragment: Fragment value to validate.
        :return: True if fragment is valid.
        """
        # if GenericValidator.is_blank_or_null(fragment):
        if fragment is None or fragment.strip() == '':
            return True

        return self.__is_off(self.NO_FRAGMENTS)
    
    def _is_valid_path(self, path: str):
        """
        Returns true if the path is valid.  A value of None is considered invalid.

        :param path: Path value to validate.
        :return: True if path is valid.
        """
        if path is None or not self.__PATH_PATTERN.fullmatch(path):
            return False
        
        parts = path.split('/')
        depth = 0

        for part in parts:
            if part == "..":
                depth -= 1
                if depth < 0:
                    return False
            elif part and part != ".":
                depth += 1
            
            if self.__is_off(self.ALLOW_2_SLASHES) and "//" in path:
                return False
        
        return True
    
    def _is_valid_query(self, query: str):
        """
        Returns true if the query is None, or it's a properly formatted query string.
        
        :param query: Query value to validate.
        :return: True if query is valid.
        """
        if not query:
            return True

        return bool(self.__QUERY_PATTERN.fullmatch(query))
    
    def _is_valid_scheme(self, scheme: str):
        """
        Validate scheme. If schemes[] was initialized to a non-None value,
        then only those schemes are allowed.
        Otherwise, the default schemes are "http", "https", "ftp".
        Matching is case-blind.

        :param scheme: The scheme to validate.  A value of None is considered invalid.
        :return: True if valid.
        """
        if not scheme or not self.__SCHEME_PATTERN.fullmatch(scheme):
            return False
        if self.__is_off(self.ALLOW_ALL_SCHEMES) and scheme.lower() not in self.__allowed_schemes:
            return False
        return True
