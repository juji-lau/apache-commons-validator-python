from typing import Dict, Any, Optional, Final
import sys
import threading
from src.main.validator_results import ValidatorResults
from src.main.validator_exception import ValidatorException


class Validator:
    serializable = True

    BEAN_PARAM: Final[str] = "object"
    #: Resources key the JavaBean is stored to perform validation on.

    VALIDATOR_ACTION_PARAM: Final[str] = "src.main.ValidatorAction"
    #: Resources key the ValidatorAction is stored under.

    VALIDATOR_RESULTS_PARAM: Final[str] = "src.main.ValidatorResults"
    #: Resources key the ValidatorResults is stored under.

    FORM_PARAM: Final[str] = "src.main.Form"
    #: Resources key the Form is stored under.

    FIELD_PARAM: Final[str] = "src.main.Field"
    #: Resources key the Field is stored under.

    VALIDATOR_PARAM: Final[str] = "src.main.Validator"
    #: Resources key the Validator is stored under.

    LOCALE_PARAM: Final[str] = "locale"
    #: Resources key the Locale is stored.

    def __init__(
        self,
        resources,
        form_name: Optional[str] = None,
        field_name: Optional[str] = None,
    ):
        if resources is None:
            raise ValueError("resources cannot be None.")
        elif resources is not None and form_name is None and field_name is not None:
            raise ValueError(
                "form_name cannot be None if resources and field_name are not None."
            )

        self.__resources = resources
        #: The Validator Resources.

        self.__form_name = form_name
        #: The name of the form to validate.

        self.__field_name = field_name
        #: The name of the field on the form to validate.

        self.__parameters: Dict[str, Any] = {}
        #: Maps validation method parameter class names to objects.

        self.__page = 0
        #: The current page number to validate.

        self.__class_loader = None
        #: The class loader to use for instantiating application objects.

        self.__use_context_class_loader = False
        #: Whether or not to use the Context ClassLoader.

        self.__only_return_errors = False
        #: Whether to return only failed validation fields.

    def clear(self):
        """Clears form name, field name, parameters, and resets page.
        (translation of clear())"""
        self.__form_name = None
        self.__field_name = None
        self.__parameters.clear()
        self.__page = 0

    def get_class_loader(self):
        """
        Gets the class loader for instantiating application objects.
        (translation of getClassLoader())
        """
        if self.__class_loader:
            return self.__class_loader

        if self.use_context_class_loader:
            # TODO: replace with importlib functionality to import dynamic run time classes
            # In Python, class loaders are not handled the same way
            try:
                context_loader = sys.modules.get(
                    threading.current_thread().__class__.__module__
                )
                if context_loader is not None:
                    return context_loader
            except Exception:
                pass

        return sys.modules[self.__class__.__module__]

    @property
    def field_name(self) -> Optional[str]:
        """Gets the field name. (translation of getFieldName())"""
        return self.__field_name

    @property
    def form_name(self) -> Optional[str]:
        """Gets the form name. (translation of getFormName())"""
        return self.__form_name

    @property
    def only_return_errors(self) -> bool:
        """Returns whether only failed fields are returned.
        (translation of getOnlyReturnErrors())"""
        return self.__only_return_errors

    @property
    def page(self) -> int:
        """
        Gets the current page number.

        This, in conjunction with the page property of a Field,
        can control the processing of fields. If the field's
        page is less than or equal to this page value, it will be processed.

        (translation of getPage())
        """
        return self.__page

    @property
    def parameters(self) -> Dict[str, Any]:
        """Gets the validation method parameters. (translation of getParameters())"""
        return self.__parameters

    def get_parameter_value(self, parameter_class_name: str) -> Any:
        """
        Gets the value of the specified parameter that will be used during the
        processing of validations. (translation of getParameterValue())

        Method Arguments:
            parameter_class_name (str): the full class name of the parameter of
                                        the validation method that corresponds
                                        to the value/instance passed in with it
        """
        return self.parameters.get(parameter_class_name)

    @property
    def resources(self):
        """Gets the validator resources. (translation of getResources())"""
        return self.__resources

    @property
    def use_context_class_loader(self) -> bool:
        """Returns whether the context class loader should be used."""
        return self.__use_context_class_loader

    def set_class_loader(self, class_loader):
        """Sets the class loader for instantiating application objects."""
        self.__class_loader = class_loader

    @field_name.setter
    def field_name(self, field_name: str):
        """Sets the field name for validation. (translation of setFieldName())"""
        self.__field_name = field_name

    @form_name.setter
    def form_name(self, form_name: str):
        """Sets the form name for validation. (translation of setFormName())"""
        self.__form_name = form_name

    @only_return_errors.setter
    def only_return_errors(self, only_return_errors: bool):
        """Configures whether only failed fields are returned.
        (translation of setOnlyReturnErrors())"""
        self.__only_return_errors = only_return_errors

    @page.setter
    def page(self, page: int):
        """Sets the current page number. (translation of setPage())"""
        self.__page = page

    def set_parameter(self, parameter_class_name: str, parameter_value: Any):
        """Sets a parameter for a validation method.
        (translation of setParameter())"""
        self.parameters[parameter_class_name] = parameter_value

    @use_context_class_loader.setter
    def use_context_class_loader(self, use_context_class_loader: bool):
        """Sets whether to use the Context ClassLoader."""
        self.__use_context_class_loader = use_context_class_loader

    def validate(self) -> ValidatorResults | ValidatorException:
        """Performs validations based on the configured resources.

        Returns: a dict that uses the property of the Field for the key and
        and the number of errors the field had for the value; throws
        ValidatorException if an error occurs during validation
        """
        locale = self.get_parameter_value(self.LOCALE_PARAM)
        if locale is None:
            import locale as py_locale

            locale = py_locale.getdefaultlocale()[0]

        self.set_parameter(self.VALIDATOR_PARAM, self)

        form = self.resources.get_form(locale, self.form_name)

        if form is not None:
            self.set_parameter(self.FORM_PARAM, form)
            return form.validate(
                self.parameters,
                self.resources.get_validator_actions(),
                self.page,
                self.field_name,
            )

        return ValidatorResults()
