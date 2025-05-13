from typing import Final, Iterator
from types import MappingProxyType

class ValidatorResult:
    """Contains the results of a set of validation rules processed on a JavaBean."""

    class ResultStatus:
        """Contains the status of a validation."""

        def __init__(self, valid: bool, result: object = None):
            self._valid = valid
            self._result = result
            self.serializable = True
            self.cloneable = False

        @property
        def valid(self) -> bool:
            return self._valid

        @valid.setter
        def valid(self, valid: bool):
            self._valid = valid

        @property
        def result(self) -> object:
            return self._result

        @result.setter
        def result(self, result: object):
            self._result = result

    def __init__(self, field):
        """Constructs a ValidatorResult with the associated field being validated.

        Args:
            field: The field that was validated.
        """
        self._field = field
        self._h_actions = {}
        self.serializable = True

    @property
    def field(self):
        """The field that was validated."""
        return self._field

    def add(self, validator_name: str, result: bool, value: object = None):
        """Add the result of a validator action.

        Args:
            validator_name (str): Name of the validator.
            result (bool): Whether the validation passed.
            value (object, optional): Value returned by the validator.
        """
        self._h_actions[validator_name] = ValidatorResult.ResultStatus(result, value)

    def contains_action(self, validator_name: str) -> bool:
        """Indicates whether a specified validator is in the result.

        Args:
            validator_name (str): Name of the validator.

        Returns:
            bool: True if the validator is in the result; False otherwise.
        """
        return validator_name in self._h_actions

    def get_actions(self) -> Iterator[str]:
        """Gets an iterator of the action names contained in this result.

        Returns:
            Iterator[str]: An iterator over the validator action names.
        """
        return iter(self._h_actions.keys())

    def get_action_map(self) -> MappingProxyType:
        """Gets an unmodifiable mapping of validator actions.

        Returns:
            MappingProxyType: A read-only dictionary mapping validator names to ResultStatus objects.
        """
        return MappingProxyType(self._h_actions)

    def get_result(self, validator_name: str):
        """Gets the result of a validation.

        Args:
            validator_name (str): Name of the validator.

        Returns:
            object: The result returned by the validator, or None if not found.
        """
        status: Final[ValidatorResult.ResultStatus] = self._h_actions.get(validator_name)
        return None if status is None else status.result

    def is_valid(self, validator_name: str) -> bool:
        """Indicates whether a specified validation passed.

        Args:
            validator_name (str): Name of the validator.

        Returns:
            bool: True if the validation passed; False otherwise.
        """
        status: Final[ValidatorResult.ResultStatus] = self._h_actions.get(validator_name)
        return status is not None and status.valid