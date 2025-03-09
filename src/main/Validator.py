from typing import Dict, Any, Optional, Final
from src.main.ValidatorResults import ValidatorResults

class Validator:
    serializable = True
    
    #: Resources key the JavaBean is stored to perform validation on.
    BEAN_PARAM: Final[str] = "object"
    
    #: Resources key the ValidatorAction is stored under.
    VALIDATOR_ACTION_PARAM: Final[str] = "src.main.ValidatorAction"
    
    #: Resources key the ValidatorResults is stored under.
    VALIDATOR_RESULTS_PARAM: Final[str] = "src.main.ValidatorResults"
    
    #: Resources key the Form is stored under.
    FORM_PARAM: Final[str] = "src.main.Form"
    
    #: Resources key the Field is stored under.
    FIELD_PARAM: Final[str] = "src.main.Field"
    
    #: Resources key the Validator is stored under.
    VALIDATOR_PARAM: Final[str] = "src.main.Validator"
    
    #: Resources key the Locale is stored.
    LOCALE_PARAM: Final[str] = "locale"
    
    def __init__(self, resources, form_name: Optional[str] = None, field_name: Optional[str] = None):
        if resources is None:
            raise ValueError("resources cannot be None.")
        elif resources is not None and form_name is None and field_name is not None:
            raise ValueError("form_name cannot be None if resources and field_name are not None.")

        #: The Validator Resources.
        self._resources = resources
        
        #: The name of the form to validate.
        self._form_name = form_name
        
        #: The name of the field on the form to validate.
        self.field_name = field_name
        
        #: Maps validation method parameter class names to objects.
        self._parameters: Dict[str, Any] = {}
        
        #: The current page number to validate.
        self._page = 0
        
        #: The class loader to use for instantiating application objects.
        self._class_loader = None
        
        #: Whether or not to use the Context ClassLoader.
        self._use_context_class_loader = False
        
        #: Whether to return only failed validation fields.
        self._only_return_errors = False
    
    def clear(self):
        """Clears form name, field name, parameters, and resets page."""
        self.form_name = None
        self.field_name = None
        self.parameters.clear()
        self.page = 0
    
    def get_class_loader(self):
        """Gets the class loader for instantiating application objects."""
        if self.class_loader:
            return self.class_loader
        
        if self.use_context_class_loader:
            # TODO: replace with importlib functionality to import dynamic run time classes 
            return None  # In Python, class loaders are not handled the same way
        
        return None
    
    def get_field_name(self) -> Optional[str]:
        """Gets the field name."""
        return self.field_name
    
    def get_form_name(self) -> Optional[str]:
        """Gets the form name."""
        return self.form_name
    
    def get_only_return_errors(self) -> bool:
        """Returns whether only failed fields are returned."""
        return self.only_return_errors
    
    def get_page(self) -> int:
        """Gets the current page number."""
        return self.page
    
    def get_parameters(self) -> Dict[str, Any]:
        """Gets the validation method parameters."""
        return self.parameters
    
    def get_parameter_value(self, parameter_class_name: str) -> Any:
        """Gets the value of the specified validation parameter."""
        return self.parameters.get(parameter_class_name)
    
    def get_resources(self):
        """Gets the validator resources."""
        return self.resources
    
    def get_use_context_class_loader(self) -> bool:
        """Returns whether the context class loader should be used."""
        return self.use_context_class_loader
    
    def set_class_loader(self, class_loader):
        """Sets the class loader for instantiating application objects."""
        self.class_loader = class_loader
    
    def set_field_name(self, field_name: str):
        """Sets the field name for validation."""
        self.field_name = field_name
    
    def set_form_name(self, form_name: str):
        """Sets the form name for validation."""
        self.form_name = form_name
    
    def set_only_return_errors(self, only_return_errors: bool):
        """Configures whether only failed fields are returned."""
        self.only_return_errors = only_return_errors
    
    def set_page(self, page: int):
        """Sets the current page number."""
        self.page = page
    
    def set_parameter(self, parameter_class_name: str, parameter_value: Any):
        """Sets a parameter for a validation method."""
        self.parameters[parameter_class_name] = parameter_value
    
    def set_use_context_class_loader(self, use_context_class_loader: bool):
        """Sets whether to use the Context ClassLoader."""
        self.use_context_class_loader = use_context_class_loader
    
    def validate(self):
        """Performs validations based on the configured resources."""
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
                self.field_name
            )
        
        return ValidatorResults()