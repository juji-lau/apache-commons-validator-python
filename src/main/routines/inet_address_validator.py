"""
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
from ..routines.regex_validator import RegexValidator
# from ..generic_validator import GenericValidator

class InetAddressValidator:
    """
    InetAddress validation and conversion routines.

    This class provides methods to validate a candidate IP address.

    This class is a Singleton; you can retrieve the instance via the {@link #getInstance()} method.
    """
    serializable = True

    __MAX_BYTE: Final[int] = 128
    __IPV4_MAX_OCTET_VALUE: Final[int] = 255
    __MAX_UNSIGNED_SHORT: Final[int] = 0xffff
    __BASE_16: Final[int] = 16
    __IPV4_REGEX: Final[str] = r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$"

    # Max number of hex groups (separated by :) in an IPV6 address
    __IPV6_MAX_HEX_GROUPS: Final[int] = 8

    # Max hex digits in each IPv6 group
    __IPV6_MAX_HEX_DIGITS_PER_GROUP: Final[int] = 4

    __VALIDATOR = None

    __DIGITS_PATTERN = re.compile(r"\d{1,3}")

    __ID_CHECK_PATTERN = re.compile(r"[^\s/%]+")

    __IPV4_VALIDATOR: Final[RegexValidator] = RegexValidator(__IPV4_REGEX)

    @classmethod
    def get_instance(cls):
        """
        Returns the singleton instance of this validator.

        :return: The singleton instance of this validator.
        """
        if not cls.__VALIDATOR:
            cls.__VALIDATOR = InetAddressValidator()
        return cls.__VALIDATOR
    
    def __init__(self):
        """
        Constructs a new instanse.
        """
        pass

    def is_valid(self, inet_address: str):
        """
        Checks if the specified string is a valid IPv4 or IPv6 address.
    
        :param inet_address: the string to validate.
        :return: True if the string validates as an IP address.
        """
        return self.is_valid_inet4_address(inet_address) or self.is_valid_inet6_address(inet_address)
    
    def is_valid_inet4_address(self, inet4_address: str):
        """
        Validates an IPv4 address. Returns True if valid.
     
        :param inet4_address: The IPv4 address to validate.
        :return: True if the argument contains a valid IPv4 address.
        """
        # verify that address conforms to generic IPv4 format
        groups = self.__IPV4_VALIDATOR.match(inet4_address)
        if not groups:
            return False
        
        # verify that address subgroups are legal
        for ip_segment in groups:
            # if GenericValidator.is_blank_or_null(ip_segment):
            if ip_segment is None or ip_segment == '':
                return False
            
            i_ip_segment = 0
            try:
                i_ip_segment = int(ip_segment)
            except ValueError:
                return False
            if i_ip_segment > self.__IPV4_MAX_OCTET_VALUE or (len(ip_segment) > 1 and ip_segment.startswith('0')):
                return False
            
        return True
        
    def is_valid_inet6_address(self, inet6_address: str):
        """
        Validates an IPv6 address. Returns true if valid.

        :param inet6_address: The IPv6 address to validate.
        :return: True if the argument contains a valid IPv6 address.
        """
        # remove prefix size; this will appear after the zone id (if any)
        parts = inet6_address.split('/', -1)
        if len(parts) > 2:          # can only have one prefix specifier
            return False

        if len(parts) == 2:
            if not self.__DIGITS_PATTERN.fullmatch(parts[1]):
                return False
            
            bits = int(parts[1])    # cannot fail because of re check
            if bits < 0 or bits > self.__MAX_BYTE:
                return False        # out of range
            
        # remove zone-id
        parts = parts[0].split('%', -1)
        # The id syntax is implementation independent, but it presumably cannot allow:
        # whitespace, '/' or '%'
        if len(parts) > 2 or (len(parts) == 2 and not self.__ID_CHECK_PATTERN.fullmatch(parts[1])):
            return False
        
        inet6_address = parts[0]
        contains_compressed_zeroes = "::" in inet6_address
        if contains_compressed_zeroes and inet6_address.count("::") > 1:
            return False
        
        starts_with_compressed = inet6_address.startswith("::")
        starts_with_sep = inet6_address.startswith(':')
        ends_with_compressed = inet6_address.endswith("::")
        ends_with_sep = inet6_address.endswith(':')
        if (starts_with_sep and not starts_with_compressed) or (ends_with_sep and not ends_with_compressed):
            return False
        
        octets = inet6_address.split(':')
        if contains_compressed_zeroes:
            octet_list = list(octets)
            if ends_with_compressed:
                octet_list = octet_list[:-1]
            if starts_with_compressed and octet_list:
                octet_list.pop(0)
            octets = octet_list
        
        if len(octets) > self.__IPV6_MAX_HEX_GROUPS:
            return False
        
        valid_octets = 0
        empty_octets  = 0 # consecutive empty chunks
        for index, octet in enumerate(octets):
            # if GenericValidator.is_blank_or_null(octet):
            if octet is None or octet == '':
                empty_octets += 1
                if empty_octets > 1:
                    return False
            else:
                empty_octets = 0
                # Is last chunk an IPv4 address?
                if index == len(octets) - 1 and '.' in octet:
                    if not self.is_valid_inet4_address(octet):
                        return False
                    valid_octets += 2
                    continue

                if len(octet) > self.__IPV6_MAX_HEX_DIGITS_PER_GROUP:
                    return False
                
                octet_int = 0
                try:
                    octet_int = int(octet, self.__BASE_16)
                except ValueError:
                    return False
                if octet_int < 0 or octet_int > self.__MAX_UNSIGNED_SHORT:
                    return False
                
            valid_octets += 1

        if valid_octets > self.__IPV6_MAX_HEX_GROUPS or (valid_octets < self.__IPV6_MAX_HEX_GROUPS and not contains_compressed_zeroes):
            return False

        return True
