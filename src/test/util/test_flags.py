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

from src.main.util.flags import Flags
from typing import Final
import copy

# Declare some flags for testing
_LONG_FLAG: Final[int] = 1
_LONG_FLAG_2: Final[int] = 2
_INT_FLAG: Final[int] = 4

class FlagsTest:

    def __init__(self):
        pass

    def test_get_flags(self):
        f: Final[Flags] = Flags(45)
        assert 45 == f.flags

    def test_clear(self):
        f: Final[Flags] = Flags(98432)
        f.clear()
        assert 0 == f.flags

    def test_hash_code(self):
        f: Final[Flags] = Flags(45)
        assert hash(f) == 45

    def test_is_on_is_false_when_not_all_flags_are_one(self):
        first: Final[Flags] = Flags(1)
        first_and_second: Final[int] = 3
        assert first.is_on(first_and_second) is False
    
    def test_is_on_is_true_when_high_order_bit_is_set_and_queried(self):
        all_on: Final[Flags] = Flags(~0)
        high_order: Final[int] = 0x8000000000000000
        assert all_on.is_on(high_order) is True
    
    def test_is_on_off(self):
        f: Final[Flags] = Flags()
        f.turn_on(_LONG_FLAG)
        f.turn_on(_INT_FLAG)
        assert f.is_on(_LONG_FLAG) is True
        assert f.is_off(_LONG_FLAG) is False

        assert f.is_on(_INT_FLAG) is True
        assert f.is_off(_INT_FLAG) is False

        assert f.is_off(_LONG_FLAG_2) is True
    
    def test_string(self):
        f: Final[Flags] = Flags()
        s = str(f)
        assert len(s) == 64
        assert s == "0000000000000000000000000000000000000000000000000000000000000000"

        f.turn_on_all()
        s = str(f)
        assert s == "1111111111111111111111111111111111111111111111111111111111111111"

        f.turn_off_all()
        f.turn_on(_INT_FLAG)
        s = str(f)
        assert len(s) == 64
        assert s == "0000000000000000000000000000000000000000000000000000000000000100"

    def test_turn_off_all(self):
        f: Final[Flags] = Flags(98432)
        f.turn_off_all()
        assert f.flags == 0
    
    def test_turn_on_all(self):
        f: Final[Flags] = Flags()
        f.turn_on_all()
        assert f.flags == 0xFFFFFFFFFFFFFFFF
    
    def test_copy_and_eq(self):
        f: Final[Flags] = Flags(4)
        c: Final[Flags] = copy.copy(f)
        assert (f == c) is True

t = FlagsTest()
t.test_get_flags()
t.test_clear()
t.test_hash_code()
t.test_is_on_is_false_when_not_all_flags_are_one()
t.test_is_on_is_true_when_high_order_bit_is_set_and_queried()
t.test_is_on_off()
t.test_string()
t.test_turn_off_all()
t.test_turn_on_all()
t.test_copy_and_eq()
