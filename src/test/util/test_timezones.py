""" 
Module Name: test_timezones.py
Description: Translates apache.commons-validator.test.validator.util.TestTimeZones.java
    Link: https://github.com/apache/commons-validator/blob/master/src/test/java/org/apache/commons/validator/util/TestTimeZones.java
    TimeZone test fixtures.

    This module provides timezone constants for testing purposes, similar to 
    the functionality of org.apache.commons.validator.util.TestTimeZones in Java.
    The module defines fixtures for Eastern Standard Time (EST), Eastern European 
    Time (EET), and Coordinated Universal Time (UTC).

    For Python 3.9+ the IANA Time Zone Database is accessed via the zoneinfo module.
    For earlier versions or if zoneinfo is not available, this module falls back to 
    using a fixed-offset timezone created with datetime.timezone.


Author: Juji Lau
License:
    Licensed to the Apache Software Foundation (ASF) under one or more
    contributor license agreements. See the NOTICE file distributed with
    this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0
    (the "License"); you may not use this file except in compliance with
    the License. You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
Changes:
    Added serializeable and clone as abstract attributes

"""

from datetime import tzinfo, timezone, timedelta
from zoneinfo import ZoneInfo


class TestTimeZones:
    """
    TimeZone Test fixtures.
    """
    # EST = timezone(timedelta(hours=-5), name="EST")
    EST = ZoneInfo("America/New_York")      # Fails a test case because dateparser.parse() cannot recognize timezone(timedelta(hours=-5), name="EST") as EST.
    EET = timezone(timedelta(hours=+2), name="EET")
    UTC = timezone.utc
    GMT = timezone(timedelta(hours=0), name="GMT")