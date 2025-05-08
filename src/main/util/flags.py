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
class Flags:
    """
    Represents a collection of 64 boolean (on/off) flags.  Individual flags
    are represented by powers of 2.  For example,
    Flag 1 = 1
    Flag 2 = 2
    Flag 3 = 4
    Flag 4 = 8

    or using shift operator to make numbering easier:
    Flag 1 = 1 << 0
    Flag 2 = 1 << 1
    Flag 3 = 1 << 2
    Flag 4 = 1 << 3

    There cannot be a flag with a value of 3 because that represents Flag 1
    and Flag 2 both being on/true.
    """

    def __init__(self, flags=0):
        self._flags = flags
        self.serializable = True
        self.clonable = True

    def clear(self):
        """
        Turns off all flags. This is a synonym for `turnOffAll()`
        """
        self._flags = 0

    def __copy__(self):
        """
        Clone this Flags object.

        :return: a copy of this object.
        """
        return Flags(self._flags)

    def __eq__(self, other):
        """
        Tests if two Flags objects are in the same state.

        :param other: object being tested
        :return: whether the flags are equal.
        """
        if not isinstance(other, Flags):
            return False
        return self._flags == other._flags

    @property
    def flags(self):
        """
        Returns the current flags.
        :return: collection of boolean flags represented.
        """
        return self._flags

    def __hash__(self):
        """
        The hash code is based on the current state of the flags.

        :return: the hash code for this object.
        """
        return hash(self._flags)
    def is_off(self, flag):
        """
        Tests whether the given flag is off. If the flag is not a power of 2
        (for example, 3) this tests whether the combination of flags is off.

        :param flag: Flag value to check.
        :return: whether the specified flag value is off.
        """
        return (self._flags & flag) == 0
    def is_on(self, flag):
        """
        Tests whether the given flag is on. If the flag is not a power of 2
        for example, 3) this tests whether the combination of flags is on.
        :param flag: Flag value to check.
        :return: whether the specified flag value is on.
        """
        return (self._flags & flag) == flag
    def __str__(self):
        """
        Returns a 64 length String with the first flag on the right and the
        64th flag on the left. A 1 indicates the flag is on, a 0 means it's
        off.

        :return: string representation of this object.
        """
        return str(bin(self._flags)[2:]).zfill(
            64
        )  # convert to binary then pad string to 64 chars by prepending 0s

    def turn_off(self, flag):
        """
        Turns off the given flag. If the flag is not a power of 2 (for example, 3) this
        turns off multiple flags.

        :param flag: Flag value to turn off.
        """
        self._flags &= ~flag

    def turn_off_all(self):
        """
        Turn off all flags.
        """
        self._flags = 0
    def turn_on(self, flag):
        """
        Turns on the given flag. If the flag is not a power of 2 (for example, 3) this
        turns on multiple flags.

        :param flag: Flag value to turn on.
        """
        self._flags |= flag

    def turn_on_all(self):
        """
        Turn on all 64 flags.
        """
        self._flags = 0xFFFFFFFFFFFFFFFF
