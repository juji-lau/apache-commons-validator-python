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

from src.apache_commons_validator_python.routines.percent_validator import PercentValidator
from src.apache_commons_validator_python.routines.abstract_number_validator import AbstractNumberValidator

class TestPercentValidator:

    def test_format_type(self):
        assert PercentValidator.get_instance().format_type == 2
        assert PercentValidator.get_instance().format_type == AbstractNumberValidator.PERCENT_FORMAT

    def test_invalid(self):
        validator = PercentValidator()

        # Invalid missing
        assert validator.is_valid(None) is False, f"FAILED: is_valid(None) expected False but got True"
        assert validator.is_valid('') is False, f"FAILED: is_valid() expected False but got True"
        assert validator.validate(None) is None, f"FAILED: validate(None) expected None but got {validator.validate(None)}"
        assert validator.validate('') is None, f"FAILED: validate() expected None but got {validator.validate('')}"

        # Invalid UK
        assert validator.is_valid("12@", locale="en_GB.UTF-8") is False, f"FAILED: is_valid('12@', locale='en_GB.UTF-8') expected False but got True"
        assert validator.is_valid("(12%)", locale="en_GB.UTF-8") is False, f"FAILED: is_valid('(12%)', locale='en_GB.UTF-8') expected False but got True"

        # Invalid US
        assert validator.is_valid("12@", locale="en_US.UTF-8") is False, f"FAILED: is_valid('12@', locale='en_US.UTF-8') expected False but got True"
        assert validator.is_valid("(12%)", locale="en_US.UTF-8") is False, f"FAILED: is_valid('(12%)', locale='en_US.UTF-8') expected False but got True"
    
    def test_valid(self):
        validator = PercentValidator.get_instance()
        validator_not_strict = PercentValidator(False)
        expected = 0.12
        negative = -0.12
        hundred = 1.00
        frac = 0.125

        assert validator.validate("12%") == expected, f"FAILED: validate('12%') expected {expected} but got {validator.validate('12%')}"
        assert validator.validate("-12%") == negative, f"FAILED: validate('-12%') expected {negative} but got {validator.validate('-12%')}"
        assert validator.validate("100%") == hundred, f"FAILED: validate('100%') expected {hundred} but got {validator.validate('100%')}"
        assert validator_not_strict.validate("12.5%") == frac, f"FAILED: validate('12.5%') expected {frac} but got {validator_not_strict.validate('12.5%')}"

        # Valid UK
        assert validator.validate("12%", locale="en_GB.UTF-8") == expected, f"FAILED: validate('12%', locale='en_GB.UTF-8') expected {expected} but got {validator.validate('12%', locale='en_GB.UTF-8')}"
        assert validator.validate("-12%", locale="en_GB.UTF-8") == negative, f"FAILED: validate('-12%', locale='en_GB.UTF-8') expected {negative} but got {validator.validate('-12%', locale='en_GB.UTF-8')}"
        assert validator.validate("12", locale="en_GB.UTF-8") == expected, f"FAILED: validate('100%', locale='en_GB.UTF-8') expected {hundred} but got {validator.validate('100%', locale='en_US.UTF-8')}"

        # Valid US
        assert validator.validate("12%", locale="en_US.UTF-8") == expected, f"FAILED: validate('12%', locale='en_US.UTF-8') expected {expected} but got {validator.validate('12%', locale='en_US.UTF-8')}"
        assert validator.validate("-12%", locale="en_US.UTF-8") == negative, f"FAILED: validate('-12%', locale='en_US.UTF-8') expected {negative} but got {validator.validate('-12%', locale='en_US.UTF-8')}"
        assert validator.validate("12", locale="en_US.UTF-8") == expected, f"FAILED: validate('100%', locale='en_US.UTF-8') expected {hundred} but got {validator.validate('100%', locale='en_US.UTF-8')}"