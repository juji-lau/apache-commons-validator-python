"""
Module Name: test_date_validator.py
Description:
    This file contains:
        Test cases from test.java.org.apache.commons.validator.routines.DateValidatorTest.java
            Link: https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/routines/DateValidatorTest.java
        Additional test cases

Authors: Alicia Chu, Juji Lau

License (Taken from apache.commons.validator.routines.DateValidatorTest):
    Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements.
    See the NOTICE file distributed with this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License. You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software distributed under the License is
    distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and limitations under the License.

Changes:
    - Moved specific tests from TestAbstractCalendarValidator into this file (to avoid initialization errors)
    - Separated test_compare() into different test functions for better readability.
    - Moved commonly used values and objects into fixtures to leverage Pytest functionality.
"""
import pytest
from datetime import datetime, tzinfo
from dateutil.tz import gettz
from typing import Optional, Final, Callable
from src.main.routines.date_validator import DateValidator
from src.main.util.datetime_helpers import J2PyLocale
from src.test.routines.test_abstract_calendar_validator import TestAbstractCalendarValidator
from src.test.util.test_timezones import TestTimeZones

class TestDateValidator(TestAbstractCalendarValidator):
    """
    Test suite for DateValidator.

    Inherits from TestAbstractCalendarValidator to run base validation tests.

    Attributes (Additional):
        date_validator (DateValidator): The DateValidator test case.
    """

    def setup_method(self):
        self.__date_validator:DateValidator = DateValidator()
        self._validator = self.__date_validator
        self.tz = gettz("GMT")
    
    @property
    def date_validator(self):
        """ Returns this instance's date_validator."""
        return self.__date_validator

    # Constants for the test Compare methods.
    same_time = 124522
    test_date = 20050823
    
    @pytest.fixture
    def value(self) -> datetime:
        """datetime object used in multiple tests."""
        same_time = 124522
        test_date = 20050823 
        return self._create_date(self.tz, test_date, same_time)
    
    tz_gmt = gettz("GMT")
    tz_est = TestTimeZones.EST
    date20050824 = TestAbstractCalendarValidator._create_date(tz_gmt, 20050824, same_time)
    diff_hour = TestAbstractCalendarValidator._create_date(tz_gmt, test_date, 115922)
    date20050822 = TestAbstractCalendarValidator._create_date(tz_gmt, 20050822, same_time) 
    same_day_two_am = TestAbstractCalendarValidator._create_date(tz_gmt, test_date, 20000)

    # Compare dates
    @pytest.mark.parametrize (
        "compare_dt, input_tz, expected_output, assert_msg", [
            (date20050824, tz_gmt, -1,"Expected value < 2005-08-24"),
            (diff_hour, tz_gmt, 0, "Expected same date ignoring time"),
            (date20050822, tz_gmt, 1, "Expected value > 2005-08-22"),
            # Test using alternative timezone
            (date20050824, TestTimeZones.EST, -1, "Expected value to be earlier than 2005-08-24 in EST"),
            (diff_hour, TestTimeZones.EST, 0, "Expected value and diff_hour to be same date in EST"),
            (same_day_two_am, TestTimeZones.EST, 1, "Expected value to be later than 2005-08-23 02:00:00 in EST"),
            (date20050822, TestTimeZones.EST, 1, "Expected value to be later than 2005-08-22 in EST"),

        ]
    )
    def test_compare_dates(self, value:datetime, compare_dt:datetime, input_tz:tzinfo, expected_output:int, assert_msg:str) -> None:
        """ Tests the ``DateValidator.compare_dates()`` method."""
        assert self.date_validator.compare_dates(value, compare_dt, input_tz) == expected_output, assert_msg

    # Compare weeks
    date20050830 = TestAbstractCalendarValidator._create_date(tz_gmt, 20050830, same_time)
    date20050816 = TestAbstractCalendarValidator._create_date(tz_gmt, 20050816, same_time)
    @pytest.mark.parametrize (
        "compare_dt, expected_output, assert_msg", [
            (date20050830, -1,"Expected value in earlier week"),
            (date20050824, 0, "Expected same week (24th)"),
            (date20050822, 0, "Expected same week (22nd)"),
            (date20050822, 0, "Expected same week (22nd again)"),
            (date20050816, 1, "Expected value in later week"),
        ]
    )
    def test_compare_weeks(self, value:datetime, compare_dt:datetime, expected_output:int, assert_msg:str) -> None:
        """ Tests the ``DateValidator.compare_weeks()`` method."""
        assert self.date_validator.compare_weeks(value, compare_dt, self.tz) == expected_output, assert_msg
    
    # Compare months
    date20050901 = TestAbstractCalendarValidator._create_date(tz_gmt, 20050901, same_time)
    date20050801 = TestAbstractCalendarValidator._create_date(tz_gmt, 20050801, same_time)
    date20050731 = TestAbstractCalendarValidator._create_date(tz_gmt, 20050731, same_time)
    @pytest.mark.parametrize (
        "compare_dt, expected_output, assert_msg", [
            (date20050901, -1, "Expected value in earlier month"),
            (date20050830, 0,"Expected same month (30th)"),
            (date20050801, 0, "Expected same month (1st)"),
            (date20050816, 0, "Expected same month (16th)"),
            (date20050731, 1, "Expected value in later month"),
        ]
    )
    def test_compare_months(self, value:datetime, compare_dt:datetime, expected_output:int, assert_msg:str) -> None:
        """ Tests the ``DateValidator.compare_months()`` method."""
        assert self.date_validator.compare_months(value, compare_dt, self.tz) == expected_output, assert_msg


    # Compare quarters (not implemented)
    date20051101 = TestAbstractCalendarValidator._create_date(tz_gmt, 20051101, same_time)
    date20051001 = TestAbstractCalendarValidator._create_date(tz_gmt, 20051001, same_time)
    date20050701 = TestAbstractCalendarValidator._create_date(tz_gmt, 20050701, same_time)
    date20050630 = TestAbstractCalendarValidator._create_date(tz_gmt, 20050630, same_time)
    date20050110 = TestAbstractCalendarValidator._create_date(tz_gmt, 20050110, same_time) 
    @pytest.mark.parametrize (
        "compare_dt, input_month_of_first_quarter, expected_output, assert_msg", [
            # Default month_of_first_quarter (=1)
            (date20051101, 1, -1, "Expected value in earlier quarter"),
            (date20051001, 1, -1, "Expected value in earlier quarter"),
            (date20050901, 1, 0, "Expected same quarter (+1 month)"),
            (date20050701, 1, 0, "Expected same quarter"),
            (date20050731, 1, 0, "Expected same quarter (-1 month)"),
            (date20050630, 1, 1, "Expected value in later quarter"),
            # Different month_of_first_quarter (Change quarter 1 to start in Feb)
            (date20051101, 2, -1, "Expected value in earlier quarter (Feb start)"),
            (date20051001, 2, 0, "Expected same quarter (Feb start)"),
            (date20050901, 2, 0, "Expected same quarter (Feb start)"),
            (date20050701, 2, 1, "Expected value in later quarter (Feb start). value = 2005-08-23 compared to 2005-07-01 which is in Q2: May-July, value is in later quarter Aug-Oct"),
            (date20050731, 2, 1, "Expected value in later quarter (Feb start)"),
            (date20050630, 2, 1, "Expected value in later quarter (Feb start)"),
            (date20050110, 2, 1, "Expected value in later quarter (Feb start, prev year)")
        ]
    )
    def test_compare_quarters(self, value:datetime, compare_dt:datetime, input_month_of_first_quarter:int, expected_output:int, assert_msg:str) -> None:
        """ Tests the ``DateValidator.compare_quarters()`` method."""
        pass
        # assert self.__date_validator.compare_quarters(value, compare_dt, self.tz, input_month_of_first_quarter) == expected_output, assert_msg


    def test_compare_years(self, value:datetime) -> None:
        """ Tests the ``DateValidator.compare_years()`` method."""
        same_time = 124522
        assert self.date_validator.compare_years(value, self._create_date(self.tz, 20060101, same_time), self.tz) == -1, "Expected value in earlier year"
        assert self.date_validator.compare_years(value, self._create_date(self.tz, 20050101, same_time), self.tz) == 0, "Expected same year"
        assert self.date_validator.compare_years(value, self._create_date(self.tz, 20041231, same_time), self.tz) == 1, "Expected value in later year"


    # Prepare variables for the tests of validation Methods()
    @pytest.fixture
    def expected_dt(self) -> datetime:
        """Standard datetime with system default locale and timezone."""
        return self._create_calendar(None, 20051231, 0)

    @pytest.fixture
    def zone(self) -> tzinfo:
        """Different tzinfo from the system default."""
        local_offset = datetime.now().astimezone().utcoffset()
        if local_offset == TestTimeZones.EET.utcoffset(None):
            return TestTimeZones.EST
        return TestTimeZones.EET
    
    @pytest.fixture
    def expected_zone(self, zone) -> datetime:
        """Datetime with a different tzinfo that the system default."""
        return self._create_calendar(zone=zone, date=20051231, time=0)

    locale = J2PyLocale.GERMAN
    pattern = "yyyy-MM-dd"
    patternVal = "2005-12-31"
    germanPattern = "dd MMM yyyy"
    
    # 
    germanVal = "31 Dez. 2005"


    localeVal = "31.12.2005"
    defaultVal = "12/31/05"
    xxxx = "XXXX"
    default_locale = "en_US"

    @pytest.mark.parametrize (
        "assert_type, input_val, input_pattern, input_locale, assert_msg", [
            ("dt", defaultVal, None, default_locale, "validate(A) default"),
            ("dt", localeVal, None, locale, "validate(A) locale "),
            ("dt", patternVal, pattern, default_locale, "validate(A) pattern "),
            ("dt", germanVal, germanPattern, J2PyLocale.GERMAN, "validate(A) both"),
            (None, xxxx, None, default_locale, "validate(B) default"),
            (None, xxxx, None, locale, "validate(B) locale "),
            (None, xxxx, pattern, default_locale, "validate(B) pattern"),
            (None, "31 Dec 2005", germanPattern, J2PyLocale.GERMAN, "validate(B) both")
        ]
    )
    def test_validate(self, assert_type:Optional[str], expected_dt:datetime, input_val:str, input_pattern:str, input_locale:str, assert_msg:str) -> None:
        """
        Test `DateValidator.validate()`method.  
        # Also includes test cases in `test`AbstractCalendarValidatorTest.java`.
        """
        # Don't rely on specific German format - it varies between JVMs
        output_dt = DateValidator.get_instance().validate(value=input_val, pattern=input_pattern, locale=input_locale)
        if assert_type == "dt":
            assert expected_dt.date() == output_dt.date(), assert_msg
        else:
            assert output_dt is None, assert_msg

    @pytest.mark.parametrize (
        "input_val, input_pattern, input_locale, assert_msg", [
            (defaultVal, None, default_locale,  "validate(C) default"),
            (localeVal, None, locale, "validate(C) locale "),
            (patternVal, pattern, default_locale, "validate(C) pattern "),
            (germanVal, germanPattern, J2PyLocale.GERMAN, "validate(C) both"),  
        ]
    )
    def test_validate_timezone(self, expected_dt:datetime, expected_zone:datetime, zone:tzinfo, input_val, input_pattern:str, input_locale, assert_msg:str) -> None:
        """
        Test `DateValidator.is_valid()`method with a different timezone.  
        # Also includes test cases in `test`AbstractCalendarValidatorTest.java`.
        """
        # Want to check the timezone differences; can't use .time() because that's time-zone naive. 
        # Can't use .date() because that's in-sensitive to hours.
        assert expected_dt.tzinfo != expected_zone.tzinfo, f"default/EET same {zone}"
        assert expected_zone.date() == DateValidator.get_instance().validate(value=input_val, pattern=input_pattern, locale=input_locale, time_zone=zone).date(), assert_msg

    @pytest.mark.parametrize (
        "assert_type, input_val, input_pattern, input_locale, assert_msg", [
            # True
            (True, defaultVal, None, default_locale, "isValid(A) default"),
            (True, localeVal, None, locale, "isValid(A) locale "),
            (True, patternVal, pattern, default_locale, "isValid(A) pattern "),
            (True, germanVal, germanPattern, J2PyLocale.GERMAN, "isValid(A) both"),
            # False
            (False, xxxx, None, default_locale, "is_valid(B) default"),
            (False, xxxx, None, locale, "is_valid(B) locale "),
            (False, xxxx, pattern, default_locale, "is_valid(B) pattern"),
            (False, "31 Dec 2005", germanPattern, J2PyLocale.GERMAN, "is_valid(B) both")
        ]
    )
    def test_is_valid(self, assert_type:bool, input_val:str, input_pattern:str, input_locale:str, assert_msg:str) -> None:
        """
        Test `CalendarValidator.is_valid()`method.  
        # Also includes test cases in `test`AbstractCalendarValidatorTest.java`.
        """
        assert assert_type == DateValidator.get_instance().is_valid(value=input_val, pattern=input_pattern, locale=input_locale), assert_msg