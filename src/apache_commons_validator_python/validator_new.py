from typing import Any, Dict, Optional


class Validator:
    """Core class responsible for validating JavaBeans against a set of validation
    rules.

    Equivalent to org.apache.commons.validator.Validator in the Java version.
    """

    VALIDATOR_RESULTS_PARAM: str = "ValidatorResults"
    FIELD_PARAM: str = "field"

    def __init__(
        self,
        resources: 'ValidatorResources',
        form_key: str,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        self._resources = resources
        #: The Validator Resources

        self._form_key = form_key

        self._params = parameters or {}
        #: Maps validation method parameter class names to the objects to be passed into the method.

        self._page: Optional[int] = None
        #: The current page number to validate

        self._only_return_errors = False
        #: Sets this to true to not return Fields that pass validation.  Only return failures.

        self._form: Optional["Form"] = None
        #: The form to validate

        self._locale: Optional[Dict[str, str]] = None  
        #: Dict with keys: language, country, variant

    def set_only_return_errors(self, only_errors: bool) -> None:
        """Sets only_return_errors

        Args:
            only_errors (bool): if true only return fields that don't pass validation.
        """
        self._only_return_errors = only_errors

    def set_page(self, page: int) -> None:
        """Set the current page number to validate

        Args:
            page (int)
        """
        self._page = page

    def set_parameter(self, key: str, value: Any) -> None:
        """Add key, value to parameters.

        Args:
            key (str):
            value (Any)
        """
        self._params[key] = value

    def get_parameter(self, key: str) -> Any:
        """Get value for key in parameters.
        
        Args: 
            key (str)

        Returns:
            value (Any)
        """
        return self._params.get(key)

    def get_form(self) -> Optional["Form"]:
        """Returns form to validate.
        """
        return self._form

    def get_result(self) -> "ValidatorResults":
        """Get ValidatorResults of validating the form

        Raises:
            ValidatorException

        Returns:
            ValidatorResults
        """
        if self._form is None:
            self._form = self._resolve_form()

        # from ..validator_exception_new import ValidatorException
        from .validator_exception_new import ValidatorException
        if self._form is None:
            raise ValidatorException(f"Form '{self._form_key}' not found.")

        page = self._page if self._page is not None else float("inf")

        return self._form.validate(
            self._params,
            self._resources.get_validator_actions(),
            page
        )

    def _resolve_form(self) -> Optional["Form"]:
        if self._locale:
            return self._resources.get_form(
                self._locale.get("language"),
                self._locale.get("country"),
                self._locale.get("variant"),
                self._form_key
            )
        else:
            return self._resources.get_form("en", "US", None, self._form_key)

    def set_locale(self, language: str, country: str = None, variant: str = None):
        """Set the locale of the validator.

        Args:
            language (str)
            country (str, optional). Defaults to None.
            variant (str, optional). Defaults to None.
        """
        self._locale = {"language": language, "country": country, "variant": variant}

    def validate_field(self, field_name: str) -> "ValidatorResults":
        """Validate the field in the form.

        Args:
            field_name (str): field name in form to validate.

        Raises:
            ValidatorException

        Returns:
            ValidatorResults
        """
        if self._form is None:
            self._form = self._resolve_form()

        # from ..validator_exception_new import ValidatorException
        from .validator_exception_new import ValidatorException
        
        if self._form is None:
            raise ValidatorException(f"Form '{self._form_key}' not found.")

        page = self._page if self._page is not None else float("inf")

        return self._form.validate(
            self._params,
            self._resources.get_validator_actions(),
            page,
            field_name
        )