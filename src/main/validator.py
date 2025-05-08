from typing import Any, Dict, Optional


class Validator:
    """
    Core class responsible for validating JavaBeans against a set of validation rules.
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
        self._form_key = form_key
        self._params = parameters or {}
        self._page: Optional[int] = None
        self._only_return_errors = False
        self._form: Optional["Form"] = None
        self._locale: Optional[Dict[str, str]] = None  # Dict with keys: language, country, variant

    def set_only_return_errors(self, only_errors: bool):
        self._only_return_errors = only_errors

    def set_page(self, page: int):
        self._page = page

    def set_parameter(self, key: str, value: Any):
        self._params[key] = value

    def get_parameter(self, key: str) -> Any:
        return self._params.get(key)

    def get_form(self) -> Optional["Form"]:
        return self._form

    def get_result(self) -> "ValidatorResults":
        if self._form is None:
            self._form = self._resolve_form()

        from src.main.validator_exception import ValidatorException
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
        self._locale = {"language": language, "country": country, "variant": variant}

    def validate_field(self, field_name: str) -> "ValidatorResults":
        if self._form is None:
            self._form = self._resolve_form()

        from src.main.validator_exception import ValidatorException
        if self._form is None:
            raise ValidatorException(f"Form '{self._form_key}' not found.")

        page = self._page if self._page is not None else float("inf")

        return self._form.validate(
            self._params,
            self._resources.get_validator_actions(),
            page,
            field_name
        )