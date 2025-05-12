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
from typing import Dict, Set, Optional, Any
from types import MappingProxyType

class ValidatorResults:
    """
    Contains the results of a set of validation rules processed on a JavaBean.
    """

    def __init__(self):
        self._results: Dict[str, 'ValidatorResult'] = {}

    def add(self, field: 'Field', validator_name: str, result: bool, value: Optional[Any] = None):
        """
        Add the result of a validator action.

        Args:
            field (Field): The field that was validated.
            validator_name (str): The name of the validator.
            result (bool): The result of the validation.
            value (Any, optional): The value returned by the validator.
        """
        from src.main.validator_result_new import ValidatorResult
        
        key = field.key
        if key not in self._results:
            self._results[key] = ValidatorResult(field)
        self._results[key].add(validator_name, result, value)

    def get_validator_result(self, key: str) -> Optional["ValidatorResult"]:
        """
        Gets the ValidatorResult associated with the key.

        Args:
            key (str): The key generated from Field (often just the field name).

        Returns:
            ValidatorResult: The result of a specified key.
        """
        return self._results.get(key)

    def get_property_names(self) -> Set[str]:
        """
        Gets the set of property names for which at least one message has been recorded.

        Returns:
            Set[str]: An unmodifiable set of the property names.
        """
        return set(self._results.keys())

    def get_result_value_map(self) -> Dict[str, Any]:
        """
        Gets a map of any objects returned from validation routines.

        Returns:
            Dict[str, Any]: Map of objects returned by validators.
        """
        result_map = {}
        for key, validator_result in self._results.items():
            for action_name in validator_result.get_actions():
                result_map[f"{key}.{action_name}"] = validator_result.get_result(action_name)
        return result_map

    def is_empty(self) -> bool:
        """
        Gets true if there are no messages recorded in this collection.

        Returns:
            bool: Whether these results are empty.
        """
        return not self._results

    def clear(self):
        """
        Clear all results recorded by this object.
        """
        self._results.clear()

    def merge(self, other: 'ValidatorResults'):
        """
        Merge another ValidatorResults into this one.

        Args:
            other (ValidatorResults): ValidatorResults to merge.
        """
        for key, other_result in other._results.items():
            if key not in self._results:
                self._results[key] = other_result
            else:
                for action_name in other_result.get_actions():
                    result = other_result.is_valid(action_name)
                    value = other_result.get_result(action_name)
                    self._results[key].add(action_name, result, value)

    def get_action_map(self, key: str) -> Optional[MappingProxyType]:
        """
        Gets an unmodifiable mapping of validator actions for a specific field key.

        Args:
            key (str): The key generated from Field.

        Returns:
            MappingProxyType: A read-only dictionary mapping validator names to ResultStatus objects.
        """
        validator_result = self._results.get(key)
        if validator_result:
            return validator_result.get_action_map()
        return None