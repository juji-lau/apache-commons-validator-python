""" 
  Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at
 
       http://www.apache.org/licenses/LICENSE-2.0
 
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
 """
import logging
from typing import Final, Optional
from main import ValidatorException
from src.main.GenericValidator import GenericValidator
from datetime import datetime
import locale
import numpy as np
from src.main.util.utils import ValidatorUtils
from src.main.GenericTypeValidator import GenericTypeValidator

class GenericTypeValidatorImpl:
    """
    Contains validation methods for different unit tests.
    Combined validate_[type](bean, field) and validate_[type](bean, field, locale).
    """

    FIELD_TEST_NULL: Final[str] = "NULL"
    FIELD_TEST_NOTNULL: Final[str] = "NOTNULL"
    FIELD_TEST_EQUAL: Final[str] = "EQUAL"

    _logger = logging.getLogger(__name__)

    @classmethod
    def is_string_or_null(o: Optional[object]) -> bool:
        if o is None:
            return True  # This condition is not currently exercised by any tests
        return isinstance(o, str)

    @staticmethod
    def validate_byte(bean: object, field, locale: Optional[str] = None) -> bool:
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericTypeValidator.format_byte(value, locale) if locale else GenericTypeValidator.format_byte(value)

    @staticmethod
    def validate_double(bean: object, field, locale: Optional[str] = None) -> bool:
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericTypeValidator.format_double(value, locale) if locale else GenericTypeValidator.format_double(value)

    @staticmethod
    def validate_float(bean: object, field, locale: Optional[str] = None) -> bool:
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericTypeValidator.format_float(value, locale) if locale else GenericTypeValidator.format_float(value)

    @staticmethod
    def validate_int(bean: object, field, locale: Optional[str] = None) -> bool:
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericTypeValidator.format_int(value, locale) if locale else GenericTypeValidator.format_int(value)

    @staticmethod
    def validate_long(bean: object, field, locale: Optional[str] = None) -> bool:
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericTypeValidator.format_long(value, locale) if locale else GenericTypeValidator.format_long(value)

    @staticmethod
    def validate_short(bean: object, field, locale: Optional[str] = None) -> bool:
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericTypeValidator.format_short(value, locale) if locale else GenericTypeValidator.format_short(value)
