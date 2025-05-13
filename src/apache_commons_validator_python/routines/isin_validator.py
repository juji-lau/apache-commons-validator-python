"""
Module Name: isin_validator.py
Description:
    Translates apache.commons.validator.routines.ISINValidator.java

Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/ISINValidator.java

Author: Alicia Chu

License:
    Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements.
    See the NOTICE file distributed with this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software distributed under the License is
    distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and limitations under the License.

Changes:
- Locale.getISOLanguages() -> pycountry.countries.alpha_2 (ISO 3166-1 alpha-2 – two-letter country codes which are used most prominently for the Internet's country code top-level domains)
    
"""
import pycountry
from typing import Final, Optional, List
from locale import getdefaultlocale
from src.apache_commons_validator_python.routines.code_validator import CodeValidator
from src.apache_commons_validator_python.routines.checkdigit.isin_checkdigit import ISINCheckDigit


class ISINValidator:
    """Validates ISIN (International Securities Identifying Number) codes.


    Methods:
        get_instance(check_country_code): Returns a singleton instance of the validator.
        is_valid(code): Checks if the given code is a valid ISIN.
        validate(code): Returns the code if valid, otherwise None.
    """
    serializable: Final[bool] = True
    cloneable: Final[bool] = False

    _ISIN_REGEX: Final[str] = r"[A-Z]{2}[A-Z0-9]{9}[0-9]"
    _VALIDATOR: Final[CodeValidator] = CodeValidator(
        regex=_ISIN_REGEX,
        length=12,
        checkdigit=ISINCheckDigit._ISIN_CHECK_DIGIT,
    )

    # ISO 3166-1 alpha-2 – two-letter country codes(e.g. "US", "FR", "JP")
    _CCODES: Final[List[str]] = sorted([country.alpha_2 for country in pycountry.countries])

    # Extended or Fictional Codes (e.g. "EU" for European Union)
    _SPECIALS: Final[List[str]] = sorted([
        "AA",
        "AC",
        "AD",
        "AE",
        "AF",
        "AG",
        "AI",
        "AL",
        "AM",
        "AN",
        "AO",
        "AP",
        "AQ",
        "AR",
        "AS",
        "AT",
        "AU",
        "AW",
        "AX",
        "AZ",
        "BA",
        "BB",
        "BD",
        "BE",
        "BF",
        "BG",
        "BH",
        "BI",
        "BJ",
        "BL",
        "BM",
        "BN",
        "BO",
        "BQ",
        "BR",
        "BS",
        "BT",
        "BU",
        "BV",
        "BW",
        "BX",
        "BY",
        "BZ",
        "CA",
        "CC",
        "CD",
        "CF",
        "CG",
        "CH",
        "CI",
        "CK",
        "CL",
        "CM",
        "CN",
        "CO",
        "CP",
        "CQ",
        "CR",
        "CS",
        "CT",
        "CU",
        "CV",
        "CW",
        "CX",
        "CY",
        "CZ",
        "DD",
        "DE",
        "DG",
        "DJ",
        "DK",
        "DM",
        "DO",
        "DY",
        "DZ",
        "EA",
        "EC",
        "EE",
        "EF",
        "EG",
        "EH",
        "EM",
        "EP",
        "ER",
        "ES",
        "ET",
        "EU",
        "EV",
        "EW",
        "EZ",
        "FI",
        "FJ",
        "FK",
        "FL",
        "FM",
        "FO",
        "FQ",
        "FR",
        "FX",
        "GA",
        "GB",
        "GC",
        "GD",
        "GE",
        "GF",
        "GG",
        "GH",
        "GI",
        "GL",
        "GM",
        "GN",
        "GP",
        "GQ",
        "GR",
        "GS",
        "GT",
        "GU",
        "GW",
        "GY",
        "HK",
        "HM",
        "HN",
        "HR",
        "HT",
        "HU",
        "HV",
        "IB",
        "IC",
        "ID",
        "IE",
        "IL",
        "IM",
        "IN",
        "IO",
        "IQ",
        "IR",
        "IS",
        "IT",
        "JA",
        "JE",
        "JM",
        "JO",
        "JP",
        "JT",
        "KE",
        "KG",
        "KH",
        "KI",
        "KM",
        "KN",
        "KP",
        "KR",
        "KW",
        "KY",
        "KZ",
        "LA",
        "LB",
        "LC",
        "LF",
        "LI",
        "LK",
        "LR",
        "LS",
        "LT",
        "LU",
        "LV",
        "LY",
        "MA",
        "MC",
        "MD",
        "ME",
        "MF",
        "MG",
        "MH",
        "MI",
        "MK",
        "ML",
        "MM",
        "MN",
        "MO",
        "MP",
        "MQ",
        "MR",
        "MS",
        "MT",
        "MU",
        "MV",
        "MW",
        "MX",
        "MY",
        "MZ",
        "NA",
        "NC",
        "NE",
        "NF",
        "NG",
        "NH",
        "NI",
        "NL",
        "NO",
        "NP",
        "NQ",
        "NR",
        "NT",
        "NU",
        "NZ",
        "OA",
        "OM",
        "PA",
        "PC",
        "PE",
        "PF",
        "PG",
        "PH",
        "PI",
        "PK",
        "PL",
        "PM",
        "PN",
        "PR",
        "PS",
        "PT",
        "PU",
        "PW",
        "PY",
        "PZ",
        "QA",
        "QM",
        "QN",
        "QO",
        "QP",
        "QQ",
        "QR",
        "QS",
        "QT",
        "QU",
        "QV",
        "QW",
        "QX",
        "QY",
        "QZ",
        "RA",
        "RB",
        "RC",
        "RE",
        "RH",
        "RI",
        "RL",
        "RM",
        "RN",
        "RO",
        "RP",
        "RS",
        "RU",
        "RW",
        "SA",
        "SB",
        "SC",
        "SD",
        "SE",
        "SF",
        "SG",
        "SH",
        "SI",
        "SJ",
        "SK",
        "SL",
        "SM",
        "SN",
        "SO",
        "SR",
        "SS",
        "ST",
        "SU",
        "SV",
        "SX",
        "SY",
        "SZ",
        "TA",
        "TC",
        "TD",
        "TF",
        "TG",
        "TH",
        "TJ",
        "TK",
        "TL",
        "TM",
        "TN",
        "TO",
        "TP",
        "TR",
        "TT",
        "TV",
        "TW",
        "TZ",
        "UA",
        "UG",
        "UK",
        "UM",
        "UN",
        "US",
        "UY",
        "UZ",
        "VA",
        "VC",
        "VD",
        "VE",
        "VG",
        "VI",
        "VN",
        "VU",
        "WF",
        "WG",
        "WK",
        "WL",
        "WO",
        "WS",
        "WV",
        "XA",
        "XB",
        "XC",
        "XD",
        "XE",
        "XF",
        "XG",
        "XH",
        "XI",
        "XJ",
        "XK",
        "XL",
        "XM",
        "XN",
        "XO",
        "XP",
        "XQ",
        "XR",
        "XS",
        "XT",
        "XU",
        "XV",
        "XW",
        "XX",
        "XY",
        "XZ",
        "YD",
        "YE",
        "YT",
        "YU",
        "YV",
        "ZA",
        "ZM",
        "ZR",
        "ZW",
        "ZZ"
    ])

    _ISIN_VALIDATOR_FALSE: Final["ISINValidator"] = None  # to be initialized at bottom
    _ISIN_VALIDATOR_TRUE: Final["ISINValidator"] = None   # to be initialized at bottom

    def __init__(self, check_country_code: bool) -> None:
        """Initializes the ISINValidator.

        Args:
            check_country_code (bool): Whether to validate the country code prefix.
        """
        self._check_country_code: Final[bool] = check_country_code

    @classmethod
    def get_instance(cls, check_country_code: bool) -> "ISINValidator":
        """Gets the singleton instance of ISINValidator.

        Args:
            check_country_code (bool): Whether to enforce country code validation.

        Returns:
            ISINValidator: The appropriate singleton validator instance.
        """
        return cls._ISIN_VALIDATOR_TRUE if check_country_code else cls._ISIN_VALIDATOR_FALSE

    def _check_code(self, code: str) -> bool:
        """Validates the country prefix of the ISIN.

        Args:
            code (str): The two-letter ISO prefix.

        Returns:
            bool: True if the prefix is in the standard or special country code list.
        """
        return code in self._CCODES or code in self._SPECIALS

    def is_valid(self, code: Optional[str]) -> bool:
        """Checks if the provided ISIN code is valid.

        Args:
            code (str): The code to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        valid = self._VALIDATOR.is_valid(code)
        print("---------valid: ", valid)
        print("---------check country code: ", self._check_country_code)
        if valid and self._check_country_code:
            return self._check_code(code[:2])
        return valid

    def validate(self, code: Optional[str]) -> Optional[str]:
        """Validates and returns the ISIN code if valid.

        Args:
            code (str): The ISIN code to validate.

        Returns:
            Optional[str]: The valid code or None if invalid.
        """
        result = self._VALIDATOR.validate(code)
        if result and self._check_country_code:
            return result if self._check_code(code[:2]) else None
        return result


# Initialize the singleton instances
ISINValidator._ISIN_VALIDATOR_FALSE = ISINValidator(False)
ISINValidator._ISIN_VALIDATOR_TRUE = ISINValidator(True)
