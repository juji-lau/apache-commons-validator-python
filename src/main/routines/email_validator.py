"""
Module Name: email_validator.py

Description: Translates apache.commons.validator.routines.EmailValidator.java
Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/EmailValidator.java

Author: Jessica Breuhaus

License (Taken from apache.commons.validator.routines.EmailValidator.java):
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
from ..routines.domain_validator import DomainValidator
from ..routines.inet_address_validator import InetAddressValidator

class EmailValidator:
    """
    Perform email validations.

    Based on a script by Sandeep V. Tamhankar (https://javascript.internet.com)

    This implementation is not guaranteed to catch all possible errors in an email address.

    Attributes:
        <li>serializable (bool): Indicates if the object is serializable.</li>
        <li>cloneable (bool): Indicates if the object can be cloned.</li>
    """

    serializable = True
    cloneable    = False

    __VALID_CHARS: Final[str] = r"(\\.)|[^ \x00-\x1F()<>@,;:'\\\".\[\]]"
    __QUOTED_USER: Final[str] = r'"(\\\"|[^"])*"'
    __WORD: Final[str]        = r"(((" + __VALID_CHARS + r"|')+|" + __QUOTED_USER + r"))"

    __EMAIL_REGEX: Final[str]     = r"^(.+)@(\S+)$"
    __IP_DOMAIN_REGEX: Final[str] = r"^\[(.*)\]$"
    __USER_REGEX: Final[str]      = r"^" + __WORD + r"(\." + __WORD + r")*$"

    __EMAIL_PATTERN     = re.compile(__EMAIL_REGEX)
    __IP_DOMAIN_PATTERN = re.compile(__IP_DOMAIN_REGEX)
    __USER_PATTERN      = re.compile(__USER_REGEX)

    __MAX_USERNAME_LEN: Final[int] = 64

    __EMAIL_VALIDATOR = None
    """Singleton instance of this class, which doesn't consider local addresses as valid."""

    __EMAIL_VALIDATOR_WITH_TLD = None
    """Singleton instance of this class, which doesn't consider local addresses as valid."""

    __EMAIL_VALIDATOR_WITH_LOCAL = None
    """Singleton instance of this class, which does consider local addresses valid."""

    __EMAIL_VALIDATOR_WITH_LOCAL_WITH_TLD = None
    """Singleton instance of this class, which does consider local addresses valid."""

    @classmethod
    def get_instance(cls, allow_local: bool=False, allow_tld: bool=False):
        """
        Returns the Singleton instance of this validator, with local and/or TLD validation as required.

        :param allow_local: Should local addresses be considered valid? Default is False.
        :param allow_tld: Should TLDs be allowed? Default is False.
        :return: Singleton instance of this validator.
        """
        if not cls.__EMAIL_VALIDATOR:
            domain_validator_no_local = DomainValidator.get_instance(allow_local=False)
            domain_validator_local    = DomainValidator.get_instance(allow_local=True)
            cls.__EMAIL_VALIDATOR                     = EmailValidator(domain_validator=domain_validator_no_local)
            cls.__EMAIL_VALIDATOR_WITH_LOCAL          = EmailValidator(allow_local=True, domain_validator=domain_validator_local)
            cls.__EMAIL_VALIDATOR_WITH_TLD            = EmailValidator(allow_tld=True, domain_validator=domain_validator_no_local)
            cls.__EMAIL_VALIDATOR_WITH_LOCAL_WITH_TLD = EmailValidator(allow_local=True, allow_tld=True, domain_validator=domain_validator_local)
        if allow_local and allow_tld:
            return cls.__EMAIL_VALIDATOR_WITH_LOCAL_WITH_TLD
        elif allow_local:
            return cls.__EMAIL_VALIDATOR_WITH_LOCAL
        elif allow_tld:
            return cls.__EMAIL_VALIDATOR_WITH_TLD
        else:
            return cls.__EMAIL_VALIDATOR
    
    def __init__(self, allow_local: bool=False, allow_tld: bool=False, domain_validator: DomainValidator=None):
        """
        Constructor for creating instances with the specified DomainValidator.

        :param allow_local: Should local addresses be considered valid? Default is False.
        :param allow_tld: Should TLDs be allowed? Default is False.
        :param domain_validator: Allow override of the DomainValidator.
        The instance must have the same allow_local setting.
        """
        self.__allow_tld = allow_tld

        if not domain_validator:
            raise("domain_validator cannot be None")
        
        if domain_validator.allow_local != allow_local:
            raise("DomainValidator must agree with allow_local setting")
        
        self.__domain_validator = domain_validator
    
    def is_valid(self, email: str):
        """
        Checks if a field has a valid e-mail address.

        :param email: The value validation is being performed on. A value of None is considered invalid.
        :return: True if the email address is valid.
        """
        if not email or email.endswith('.'): # check this first - it's cheap!
            return False

        # Check the whole email address structure
        email_match = self.__EMAIL_PATTERN.fullmatch(email)
        if not email_match:
            return False
        
        if not self._is_valid_user(email_match.group(1)):
            return False
        
        if not self._is_valid_domain(email_match.group(2)):
            return False
        
        return True
    
    def _is_valid_domain(self, domain: str):
        """
        Returns true if the domain component of an email address is valid.
    
        :param domain: The domain being validated, may be in IDN format.
        :return: True if the email address's domain is valid.
        """
        # see if domain is an IP address in brackets
        ip_domain_match = self.__IP_DOMAIN_PATTERN.fullmatch(domain)
        if ip_domain_match:
            inet_address_validator = InetAddressValidator.get_instance()
            return inet_address_validator.is_valid(ip_domain_match.group(1))
        
        # Domain is symbolic name
        if self.__allow_tld:
            return self.__domain_validator.is_valid(domain) or ((not domain.startswith('.')) and self.__domain_validator.is_valid_tld(domain))
        
        return self.__domain_validator.is_valid(domain)
    
    def _is_valid_user(self, user: str):
        """
        Returns true if the user component of an email address is valid.

        :param user: The user being validated.
        :return: True if the username is valid.
        """
        if not user or len(user) > self.__MAX_USERNAME_LEN:
            return False
        
        return self.__USER_PATTERN.fullmatch(user)
