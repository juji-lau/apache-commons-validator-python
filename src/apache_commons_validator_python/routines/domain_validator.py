"""
Module Name: domain_validator.py

Description: Translates apache.commons.validator.routines.DomainValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/DomainValidator.java

Author: Jessica Breuhaus

License (Taken from apache.commons.validator.routines.DomainValidator.java):
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
from enum import Enum
import threading
from ..routines.regex_validator import RegexValidator
from ..util.domains import Domains

class DomainValidator:
    """Domain name validation routines.

    This validator provides methods for validating Internet domain names
    and top-level domains.

    Domain names are evaluated according to the standards of RFC1034 section 3 and RFC1123 section 2.1.
    No accommodation is provided for the specialized needs of other applications; 
    if the domain name has been URL-encoded, for example, validation will fail
    even though the equivalent plaintext version of the same name would have passed.

    Validation is also provided for top-level domains (TLDs) as defined and
    maintained by the Internet Assigned Numbers Authority (IANA):
        - is_valid_infrastructure_tld(): validates infrastructure TLDs (.arpa, etc.).
        - is_valid_generic_tld(): validates generic TLDs (.com, .org, etc.).
        - is_valid_country_code_tld(): validates country code TLDs (.us, .uk, .cn, etc.).

    (NOTE: This class does not provide IP address lookup for domain names or
    methods to ensure that a given domain name matches a specific IP; 
    see inet_address_validator.py for that functionality.)
    """
    serializable = True
    cloneable    = False

    class ArrayType(Enum):
        """Enum used by update_tld_override(ArrayType, list[str]) to determine which
        override list to update/fetch.

        Attributes:
            - GENERIC_PLUS: Update (or get a copy of) the GENERIC_TLDS_PLUS table containing additional generic TLDs.
            - GENERIC_MINUS: Update (or get a copy of) the GENERIC_TLDS_MINUS table containing deleted generic TLDs.
            - COUNTRY_CODE_PLUS: Update (or get a copy of) the COUNTRY_code_tlds_PLUS table containing additional country code TLDs.
            - COUNTRY_CODE_MINUS: Update (or get a copy of) the COUNTRY_code_tlds_MINUS table containing deleted country code TLDs.
            - GENERIC_RO: Gets a copy of the generic TLDS table.
            - COUNTRY_CODE_RO: Gets a copy of the country code table.
            - INFRASTRUCTURE_RO: Gets a copy of the infrastructure table.
            - LOCAL_RO: Gets a copy of the local table.
            - LOCAL_PLUS: Update (or get a copy of) the LOCAL_TLDS_PLUS table containing additional local TLDs.
            - LOCAL_MINUS: Update (or get a copy of) the LOCAL_TLDS_MINUS table containing deleted local TLDs.
        """
        GENERIC_PLUS = 1
        GENERIC_MINUS = 2
        COUNTRY_CODE_PLUS = 3
        COUNTRY_CODE_MINUS = 4
        GENERIC_RO = 5
        COUNTRY_CODE_RO = 6
        INFRASTRUCTURE_RO = 7
        LOCAL_RO = 8
        LOCAL_PLUS = 9
        LOCAL_MINUS = 10

    __MAX_DOMAIN_LENGTH: Final[int] = 253 # Maximum allowable length of a domain name
    __EMPTY_STRING_ARRAY: Final[list] = []

    # RFC2396: domainlabel            = alphanum | alphanum *( alphanum | "-" ) alphanum
    # Max 63 characters
    __DOMAIN_LABEL_REGEX: Final[str] = r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"

    # RFC2396 hostname = *( domainlabel "." ) toplabel [ "." ]
    # Note that the regex currently requires both a domain label and a top level label, whereas
    # the RFC does not. This is because the regex is used to detect if a TLD is present.
    # If the match fails, input is checked against DOMAIN_LABEL_REGEX (hostname_regex)
    # RFC1123 sec 2.1 allows hostnames to start with a digit
    __DOMAIN_NAME_REGEX: Final[str] = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+([a-zA-Z](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)\.?$"
    __UNEXPECTED_ENUM_VALUE: Final[str] = "Unexpected enum value: "

    # These can only be updated by the update_tld_override method, and readers must first get an instance
    # using the get_instance method which is synchronized.
    # The only other access is via get_tld_entries which is synchronized.
    __country_code_tlds_plus  = __EMPTY_STRING_ARRAY
    __generic_tlds_plus       = __EMPTY_STRING_ARRAY
    __country_code_tlds_minus = __EMPTY_STRING_ARRAY
    __generic_tlds_minus      = __EMPTY_STRING_ARRAY
    __local_tlds_minus        = __EMPTY_STRING_ARRAY
    __local_tlds_plus         = __EMPTY_STRING_ARRAY

    # The constructor is deliberately private to avoid possible problems with unsafe publication.
    # It is vital that the override lists are not mutable once they have been used in an instance
    # The lists could be copied into the instance variables, however if the lists were changed it could
    # result in different settings for the shared default instances.

    __local_tlds_minus = __EMPTY_STRING_ARRAY
    __local_tlds_plus  = __EMPTY_STRING_ARRAY

    __in_use = False
    __lock = threading.Lock()
    __DOMAIN_VALIDATOR = None
    __DOMAIN_VALIDATOR_WITH_LOCAL = None

    __INFRASTRUCTURE_TLDS: Final[list] = Domains.INFRASTRUCTURE_TLDS
    __GENERIC_TLDS: Final[list] = Domains.GENERIC_TLDS
    __COUNTRY_CODE_TLDS: Final[list] = Domains.COUNTRY_CODE_TLDS
    __LOCAL_TLDS: Final[list] = Domains.LOCAL_TLDS
    
    class Item:
        """Used to specify overrides when creating a new class."""

        def __init__(self, type, values: list[str]):
            """Constructs a new instance.

            Args:
                type (ArrayType): The ArrayType (e.g. GENERIC_PLUS, LOCAL_PLUS).
                values (list[str]): List of TLDs. Will be lower-cased and sorted.
            """
            self.type = type
            self.values = values
    
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("Use get_instance() instead")

    @classmethod
    def get_instance(cls, allow_local: bool=False, items=None):
        """Returns the singleton instance of this validator, with local validation if
        required (not by default). The user can provide a list of Item entries which can
        be used to override the generic and country code lists. Note that any such
        entries override values provided by the update_tld_override(ArrayType, str)
        method. If an entry for a particular type is not provided, then the class
        override (if any) is retained.

        Args:
            allow_local (bool): If local addresses be considered valid.
            items (list[Item]): List of Item entries.
        
        Returns:
            The singleton instance of this validator.
        """
        with cls.__lock:
            cls.__in_use = True

            if items:
                instance = super().__new__(cls)
                instance.__init_internal(allow_local, items)
                return instance

            if allow_local:
                if not cls.__DOMAIN_VALIDATOR_WITH_LOCAL:
                    instance = super().__new__(cls)
                    instance.__init_internal(allow_local, None)
                    cls.__DOMAIN_VALIDATOR_WITH_LOCAL = instance
                return cls.__DOMAIN_VALIDATOR_WITH_LOCAL
            else:
                if not cls.__DOMAIN_VALIDATOR:
                    instance = super().__new__(cls)
                    instance.__init_internal(allow_local, None)
                    cls.__DOMAIN_VALIDATOR = instance
                return cls.__DOMAIN_VALIDATOR

    @staticmethod
    def get_tld_entries(table: ArrayType):
        """Gets a copy of a class level internal list.

        Args:
            table (ArrayType): The ArrayType (any of the enum values).
        
        Returns:
            A copy of the list. Throws a `ValueError` if the table type is unexpected
                (should not happen).
        """
        with DomainValidator.__lock:
            if table == DomainValidator.ArrayType.COUNTRY_CODE_MINUS:
                return DomainValidator.__country_code_tlds_minus[:]
            elif table == DomainValidator.ArrayType.COUNTRY_CODE_PLUS:
                return DomainValidator.__country_code_tlds_plus[:]
            elif table == DomainValidator.ArrayType.GENERIC_MINUS:
                return DomainValidator.__generic_tlds_minus[:]
            elif table == DomainValidator.ArrayType.GENERIC_PLUS:
                return DomainValidator.__generic_tlds_plus[:]
            elif table == DomainValidator.ArrayType.LOCAL_MINUS:
                return DomainValidator.__local_tlds_minus[:]
            elif table == DomainValidator.ArrayType.LOCAL_PLUS:
                return DomainValidator.__local_tlds_plus[:]
            elif table == DomainValidator.ArrayType.GENERIC_RO:
                return DomainValidator.__GENERIC_TLDS[:]
            elif table == DomainValidator.ArrayType.COUNTRY_CODE_RO:
                return DomainValidator.__COUNTRY_CODE_TLDS[:]
            elif table == DomainValidator.ArrayType.INFRASTRUCTURE_RO:
                return DomainValidator.__INFRASTRUCTURE_TLDS[:]
            elif table == DomainValidator.ArrayType.LOCAL_RO:
                return DomainValidator.__LOCAL_TLDS[:]
            else:
                raise ValueError(DomainValidator.__UNEXPECTED_ENUM_VALUE + str(table))
    
    @staticmethod
    def __is_only_ascii(input: str):
        """Check if input contains only ASCII. Treats None as all ASCII.

        Args:
            input (str): The string to check.

        Returns:
            `True` if the string is only ASCII.
        """
        if not input:
            return True
        return input.isascii()
    
    @staticmethod
    def unicode_to_ascii(input: str):
        """Converts potentially Unicode input to punycode. If conversion fails, returns
        the original input.

        Args:
            input (str): The string to convert, must not be `None`.

        Returns:
            The converted input, or original input if conversion fails.
        """
        if DomainValidator.__is_only_ascii(input):
            return input
        
        try:
            # RFC3490 3.1. 1)
            # Whenever dots are used as label separators, the following
            # characters MUST be recognized as dots: U+002E (full stop), U+3002
            # (ideographic full stop), U+FF0E (fullwidth full stop), U+FF61
            # (halfwidth ideographic full stop).
            if input.endswith((
                '\u002E', # '.' full stop
                '\u3002', # ideographic full stop
                '\uFF0E', # fullwidth full stop
                '\uFF61'  # halfwidth ideographic full stop
            )):
                input = input[:-1] + '.'
            ascii_str = input.encode("idna").decode("ascii")

            if len(input) == 0: # check that there is a last character
                return input
            
            return ascii_str
        except Exception:
            return input # input is not valid
    
    @staticmethod
    def update_tld_override(table: ArrayType, tlds: list[str]):
        """Update one of the TLD override arrays. This must only be done at program
        startup, before any instances are accessed using get_instance.

        For example:
        updateTLDOverride(ArrayType.GENERIC_PLUS, "apache")
        To clear an override list, provide an empty list.

        Args:
            table (ArrayType): The table to update, see ArrayType. Must be one of the following:
                - COUNTRY_CODE_MINUS
                - COUNTRY_CODE_PLUS
                - GENERIC_MINUS
                - GENERIC_PLUS
                - LOCAL_MINUS
                - LOCAL_PLUS
            tlds (list[str]): The list of TLDs, must not be `None`.

        Returns:
            Throws an `Exception` if the validator is in use.
            Throws a `ValueError` if one of the read-only tables is requested.
        """
        if DomainValidator.__in_use:
            raise Exception("Can only invoke this method before calling get_instance")
        
        with DomainValidator.__lock:
            tlds_cpy = [tld.lower() for tld in tlds]
            tlds_cpy.sort()

            if table == DomainValidator.ArrayType.COUNTRY_CODE_MINUS:
                DomainValidator.__country_code_tlds_minus = tlds_cpy
            elif table == DomainValidator.ArrayType.COUNTRY_CODE_PLUS:
                DomainValidator.__country_code_tlds_plus = tlds_cpy
            elif table == DomainValidator.ArrayType.GENERIC_MINUS:
                DomainValidator.__generic_tlds_minus = tlds_cpy
            elif table == DomainValidator.ArrayType.GENERIC_PLUS:
                DomainValidator.__generic_tlds_plus = tlds_cpy
            elif table == DomainValidator.ArrayType.LOCAL_MINUS:
                DomainValidator.__local_tlds_minus = tlds_cpy
            elif table == DomainValidator.ArrayType.LOCAL_PLUS:
                DomainValidator.__local_tlds_plus = tlds_cpy
            elif table == DomainValidator.ArrayType.LOCAL_RO:
                raise ValueError("Cannot update the table: " + str(table))
            else:
                raise ValueError(DomainValidator.__UNEXPECTED_ENUM_VALUE + str(table))

    def __init_internal(self, allow_local: bool, items=None):
        """Private constructor."""
        self.__allow_local = allow_local

        # TLDs defined by IANA
        # Authoritative and comprehensive list at:
        # https://data.iana.org/TLD/tlds-alpha-by-domain.txt

        # Note that the above list is in UPPER case.
        # The code currently converts strings to lower case (as per the tables below).

        # IANA also provide an HTML list at http://www.iana.org/domains/root/db
        # Note that this contains several country code entries which are NOT in
        # the text file. These all have the "Not assigned" in the "Sponsoring Organisation" column
        # For example (as of 2015-01-02):
        # .bl  country-code    Not assigned
        # .um  country-code    Not assigned

        self.__domain_regex = RegexValidator(self.__DOMAIN_NAME_REGEX)
        """RegexValidator for matching domains."""

        self.__hostname_regex = RegexValidator(self.__DOMAIN_LABEL_REGEX)
        """RegexValidator for match local hostname."""
        # RFC1123 sec 2.1 allows hostnames to start with a digit

        # Local overrides
        self.__my_country_code_tlds_minus = self.__country_code_tlds_minus
        self.__my_country_code_tlds_plus = self.__country_code_tlds_plus
        self.__my_generic_tlds_minus = self.__generic_tlds_minus
        self.__my_generic_tlds_plus = self.__generic_tlds_plus
        self.__my_local_tlds_minus = self.__local_tlds_minus
        self.__my_local_tlds_plus = self.__local_tlds_plus

        if items:
            # apply the instance overrides
            for item in items:
                copy = [value.lower() for value in item.values]
                copy.sort()
                if item.type == self.ArrayType.COUNTRY_CODE_MINUS:
                    self.__my_country_code_tlds_minus = copy
                elif item.type == self.ArrayType.COUNTRY_CODE_PLUS:
                    self.__my_country_code_tlds_plus = copy
                elif item.type == self.ArrayType.GENERIC_MINUS:
                    self.__my_generic_tlds_minus = copy
                elif item.type == self.ArrayType.GENERIC_PLUS:
                    self.__my_generic_tlds_plus = copy
                elif item.type == self.ArrayType.LOCAL_MINUS:
                    self.__my_local_tlds_minus = copy
                elif item.type == self.ArrayType.LOCAL_PLUS:
                    self.__my_local_tlds_plus = copy

    def __init__(self, allow_local: bool, items=None):
        """Do not use directly. Use get_instance() instead."""
        pass
    
    def __chomp_leading_dot(self, str: str):
        """Removes the first character in the string if it is a '.'

        Args:
            str (str): The string to potentially chomp the leading dot from.
        """
        if str[0] == '.':
            return str[1:]
        return str
    
    def get_overrides(self, table: ArrayType):
        """Gets a copy of an instance level internal list.

        Args:
            table (ArrayType): The ArrayType (any of the enum values).

        Returns:
            A copy of the list. Throws a `ValueError` if the table type is
            unexpected, for example, GENERIC_RO.
        """
        if table == self.ArrayType.COUNTRY_CODE_MINUS:
            return self.__my_country_code_tlds_minus[:]
        elif table == self.ArrayType.COUNTRY_CODE_PLUS:
            return self.__my_country_code_tlds_plus[:]
        elif table == self.ArrayType.GENERIC_MINUS:
            return self.__my_generic_tlds_minus[:]
        elif table == self.ArrayType.GENERIC_PLUS:
            return self.__my_generic_tlds_plus[:]
        elif table == self.ArrayType.LOCAL_MINUS:
            return self.__my_local_tlds_minus[:]
        elif table == self.ArrayType.LOCAL_PLUS:
            return self.__my_local_tlds_plus[:]
        else:
            raise ValueError(self.__UNEXPECTED_ENUM_VALUE + str(table))

    @property
    def allow_local(self):
        """Whether or not this instance allows local addresses.

        Returns:
            `True` if local addresses are allowed.
        """
        return self.__allow_local
    
    def is_valid(self, domain: str):
        """Returns `True` if the specified domain parses as a valid domain name
        with a recognized top-level domain. The parsing is case-insensitive.

        Args:
            domain (str): The parameter to check for domain name syntax.

        Returns:
            `True` if the parameter is a valid domain name.
        """
        if not domain:
            return False
        
        domain = self.unicode_to_ascii(domain)
        # hosts must be equally reachable via punycode and Unicode
        # Unicode is never shorter than punycode, so check punycode
        # if domain did not convert, then it will be caught by ASCII
        # checks in the regexes below
        if len(domain) > self.__MAX_DOMAIN_LENGTH:
            return False
        
        groups = self.__domain_regex.match(domain)
        if groups and len(groups) > 0:
            return self.is_valid_tld(groups[0])
        
        return self.allow_local and self.__hostname_regex.is_valid(domain)
    
    def is_valid_country_code_tld(self, cc_tld: str):
        """Returns True if the specified string matches any IANA-defined country code
        top-level domain. Leading dots are ignored if present. The search is case-
        insensitive.

        Args:
            cc_tld (str): The parameter to check for country code TLD status, must not be `None`.

        Returns:
            `True` if the parameter is a country code TLD.
        """
        key = self.__chomp_leading_dot(self.unicode_to_ascii(cc_tld).lower())
        return (key in self.__COUNTRY_CODE_TLDS or key in self.__my_country_code_tlds_plus) and key not in self.__my_country_code_tlds_minus
    
    # package protected for unit test access
    # must agree with is_valid() above
    def _is_valid_domain_syntax(self, domain: str):
        """Checks if the domain syntax is valid.

        Args:
            domain (str): The parameter to check for domain name syntax.

        Returns:
            `True` if the parameter is a valid domain name.
        """
        if not domain:
            return False
        
        domain = self.unicode_to_ascii(domain)
        # hosts must be equally reachable via punycode and Unicode
        # Unicode is never shorter than punycode, so check punycode
        # if domain did not convert, then it will be caught by ASCII
        # checks in the regexes below
        if len(domain) > self.__MAX_DOMAIN_LENGTH:
            return False

        groups = self.__domain_regex.match(domain)
        return groups and len(groups) > 0 or self.__hostname_regex.is_valid(domain)

    def is_valid_generic_tld(self, g_tld: str):
        """Returns `True` if the specified string matches any IANA-defined generic top-
        level domain. Leading dots are ignored if present. The search is case-
        insensitive.

        Args:
            g_tld (str): The parameter to check for generic TLD status, must not be `None`.

        Returns:
            `True` if the parameter is a generic TLD.
        """
        key = self.__chomp_leading_dot(self.unicode_to_ascii(g_tld).lower())
        return (key in self.__GENERIC_TLDS or key in self.__my_generic_tlds_plus) and key not in self.__my_generic_tlds_minus
    
    def is_valid_infrastructure_tld(self, i_tld: str):
        """Returns `True` if the specified string matches any IANA-defined infrastructure
        top-level domain. Leading dots are ignored if present. The search is case-
        insensitive.

        Args:
            i_tld (str): The parameter to check for infrastructure TLD status, must not be `None`.

        Returns:
            `True` if the parameter is an infrastructure TLD.
        """
        key = self.__chomp_leading_dot(self.unicode_to_ascii(i_tld).lower())
        return key in self.__INFRASTRUCTURE_TLDS
    
    def is_valid_local_tld(self, l_tld: str):
        """Returns `True` if the specified string matches any widely used "local" domains
        (localhost or localdomain). Leading dots are ignored if present. The search is
        case-insensitive.

        Args:
            l_tld (str): The parameter to check for local TLD status, must not be `None`.

        Returns:
            `True` if the parameter is a local TLD.
        """
        key = self.__chomp_leading_dot(self.unicode_to_ascii(l_tld).lower())
        return (key in self.__LOCAL_TLDS or key in self.__my_local_tlds_plus) and key not in self.__my_local_tlds_minus
    
    def is_valid_tld(self, tld: str):
        """Returns `True` if the specified string matches any IANA-defined top-level
        domain. Leading dots are ignored if present. The search is case-insensitive.

        If allow_local is `True`, the TLD is checked using is_valid_local_tld(str). The
        TLD is then checked against is_valid_infrastructure_tld(str),
        is_valid_generic_tld(str) and is_valid_country_code_tld(str).

        Args:
            tld (str): The parameter to check for TLD status, must not be `None`.

        Returns:
            `True` if the parameter is a TLD.
        """
        if self.allow_local and self.is_valid_local_tld(tld):
            return True
        
        return self.is_valid_infrastructure_tld(tld) or self.is_valid_generic_tld(tld) or self.is_valid_country_code_tld(tld)
    
    @classmethod
    def __reset_singletons(cls):
        """For testing."""
        with cls.__lock:
            cls.__DOMAIN_VALIDATOR = None
            cls.__DOMAIN_VALIDATOR_WITH_LOCAL = None

