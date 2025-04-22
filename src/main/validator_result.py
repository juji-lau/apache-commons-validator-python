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

from types import MappingProxyType


class ValidatorResult:
    """
    Contains the results of a set of validation rules processed on a JavaBean.
    """

    # Got rid of _field because it wasn't being used.
    class ResultStatus:
        """
        Contains the status of a validation.
        """

        def __init__(self, valid, result):
            """
            Constructs a ResultStatus.

            Args:
                valid (bool): Whether the validator passed.
                result (object): Value returned by the validator.
            """
            self._valid = valid
            self._result = result
            self.serializable = True
            self.cloneable = False

        @property
        def valid(self):
            """Whether or not the validation passed."""
            return self._valid

        @valid.setter
        def valid(self, valid):
            self._valid = valid

        @property
        def result(self):
            """The result returned by the validator."""
            return self._result

        @result.setter
        def result(self, result):
            self._result = result

    def __init__(self, field):
        """
        Constructs a ValidatorResult with the associated field being validated.

        Args:
            field: The field that was validated.
        """
        # self._field = field
        # Internal dictionary mapping validator names to ResultStatus objects.
        self._h_action = {}
        self.serializable = True

    # @property
    # def field(self):
    #     """The field that was validated."""
    #     return self._field

    def add(self, validator_name, result, value=None):
        """
        Add the result of a validator action.

        Args:
            validator_name (str): Name of the validator.
            result (bool): Whether the validation passed.
            value (object, optional): Value returned by the validator.
        """
        self._h_action[validator_name] = ValidatorResult.ResultStatus(result, value)

    def contains_action(self, validator_name):
        """
        Indicates whether a specified validator is in the result.

        Args:
            validator_name (str): Name of the validator.

        Returns:
            bool: True if the validator is in the result; False otherwise.
        """
        return validator_name in self._h_action

    @property
    def action_map(self):
        """
        Gets an unmodifiable mapping of validator actions.

        Returns:
            MappingProxyType: A read-only dictionary mapping validator names to ResultStatus objects.
        """
        return MappingProxyType(self._h_action)

    # Deprecated
    # def get_actions(self):
    #     """
    #     Gets an iterator of the action names contained in this result.

    #     Returns:
    #         Iterator[str]: An iterator over the validator action names.
    #     """
    #     return iter(self._h_action.keys())

    def get_result(self, validator_name):
        """
        Gets the result of a validation.

        Args:
            validator_name (str): Name of the validator.

        Returns:
            object: The result returned by the validator, or None if not found.
        """
        status: Final[ResultStatus] = self._h_action.get(validator_name)
        return None if status is None else status.result

    def is_valid(self, validator_name):
        """
        Indicates whether a specified validation passed.

        Args:
            validator_name (str): Name of the validator.

        Returns:
            bool: True if the validation passed; False otherwise.
        """
        status: Final[ResultsStatus] = self._h_action.get(validator_name)
        return status is not None and status.valid
