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

from src.main.routines.percent_validator import PercentValidator

class TestPercentValidator:

    def test_invalid(self):
        validator = PercentValidator()

        # Invalid missing
        assert validator.is_valid(None) is False, f"FAILED: is_valid(None) expected False but got True"
        assert validator.is_valid('') is False, f"FAILED: is_valid() expected False but got True"
        assert validator.validate(None) is None, f"FAILED: validate(None) expected None but got {validator.validate(None)}"
        assert validator.validate('') is None, f"FAILED: validate() expected None but got {validator.validate('')}"

        # Invalid UK
        assert validator.is_valid("12@", locale="en_GB") is False, f"FAILED: is_valid('12@', locale='en_GB') expected False but got True"
        assert validator.is_valid("(12%)", locale="en_GB") is False, f"FAILED: is_valid('(12%)', locale='en_GB') expected False but got True"

        # Invalid US
        assert validator.is_valid("12@", locale="en_US") is False, f"FAILED: is_valid('12@', locale='en_US') expected False but got True"
        assert validator.is_valid("(12%)", locale="en_US") is False, f"FAILED: is_valid('(12%)', locale='en_US') expected False but got True"
    
    def test_valid(self):
        validator = PercentValidator(strict=False)
        expected = 0.12
        negative = -0.12
        hundred = 1.00
        frac = 0.125

        assert validator.validate("12%") == expected, f"FAILED: validate('12%') expected {expected} but got {validator.validate('12%')}"
        assert validator.validate("-12%") == negative, f"FAILED: validate('-12%') expected {negative} but got {validator.validate('-12%')}"
        assert validator.validate("100%") == hundred, f"FAILED: validate('100%') expected {hundred} but got {validator.validate('100%')}"
        assert validator.validate("12.5%") == frac, f"FAILED: validate('12.5%') expected {frac} but got {validator.validate('12.5%')}"

        # Valid UK
        assert validator.validate("12%", locale="en_GB") == expected, f"FAILED: validate('12%', locale='en_GB') expected {expected} but got {validator.validate('12%', locale='en_GB')}"
        assert validator.validate("-12%", locale="en_GB") == negative, f"FAILED: validate('-12%', locale='en_GB') expected {negative} but got {validator.validate('-12%', locale='en_GB')}"
        assert validator.validate("12", locale="en_GB") == expected, f"FAILED: validate('100%', locale='en_GB') expected {hundred} but got {validator.validate('100%', locale='en_US')}"

        # Valid US
        assert validator.validate("12%", locale="en_US") == expected, f"FAILED: validate('12%', locale='en_US') expected {expected} but got {validator.validate('12%', locale='en_US')}"
        assert validator.validate("-12%", locale="en_US") == negative, f"FAILED: validate('-12%', locale='en_US') expected {negative} but got {validator.validate('-12%', locale='en_US')}"
        assert validator.validate("12", locale="en_US") == expected, f"FAILED: validate('100%', locale='en_US') expected {hundred} but got {validator.validate('100%', locale='en_US')}"