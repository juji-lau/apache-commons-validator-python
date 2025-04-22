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

# TODO: add typing annotations for type

from src.main.validator_result import ValidatorResult


class ValidatorResults:
    """
    This class contains the results of a set of validation rules processed
    on a JavaBean. This is a Python adaptation of the Java version from
    Apache Commons Validator.
    """

    def __init__(self):
        # Internal dictionary mapping a field key (string) to a ValidatorResult.
        self._h_results = {}
        self.serializable = False
        self.cloneable = False

    def add(self, field: "Field", validator_name, result, value=None):
        """
        Add the result of a validator action.

        Args:
            field: The field validated. Expected to have an attribute 'key'.
            validator_name (str): The name of the validator.
            result (bool): The result of the validation.
            value (object, optional): An optional value returned by the validator.
        """
        # Retrieve the key from the field.
        # TODO: double check Field when implementeds
        key = field.key
        validator_result = self.get_validator_result(key)
        if validator_result is None:
            # Assuming ValidatorResult takes the field as an initializer argument.
            validator_result = ValidatorResult(field)
            self._h_results[key] = validator_result

        # Add the validation result to the ValidatorResult.
        validator_result.add(validator_name, result, value)

    def clear(self):
        """
        Clear all results recorded by this object.
        """
        self._h_results.clear()

    @property
    def property_names(self):
        """
        Get the set of property names for which at least one message has been recorded.

        Returns:
            frozenset: An unmodifiable set of property names.
        """
        return frozenset(self._h_results.keys())

    def get_result_value_map(self):
        """
        Gets a dictionary of any objects returned from validation routines.

        Returns:
            dict: A dictionary mapping property keys to the corresponding validator result object
                  (only if the result is not None and not a boolean).
        """
        results = {}
        for property_key, validator_result in self._h_results.items():
            for action_key in validator_result.get_actions():
                res = validator_result.get_result(action_key)
                if res is not None and not isinstance(res, bool):
                    results[property_key] = res
        return results

    def get_validator_result(self, key):
        """
        Gets the ValidatorResult associated with the given key.

        Args:
            key (str): The key generated from the Field (often just the field name).

        Returns:
            ValidatorResult or None: The result associated with the key, if present.
        """
        return self._h_results.get(key)

    def is_empty(self):
        """
        Determines if there are no messages recorded in this collection.

        Returns:
            bool: True if there are no results, False otherwise.
        """
        return not self._h_results

    def merge(self, other):
        """
        Merge another ValidatorResults instance into this one.

        Args:
            other (ValidatorResults): Another instance whose results will be merged in.
        """
        self._h_results.update(other._h_results)
