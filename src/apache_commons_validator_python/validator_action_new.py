import importlib
from typing import List, Optional

class ValidatorAction:
    """ Contains the information to dynamically create and run a validation method. 
    This is the class representation of a pluggable validator that can be defined in
    an xml file with the <validator> element.
    """

    def __init__(self):
        self.__name: Optional[str] = None
        #: The name of the validation.

        self.__class_name: Optional[str] = None
        #: The full class name of the class containing the validation method associated with this action.

        self.__method: Optional[str] = None
        #: The full method name of the validation to be performed.

        self.__depends: Optional[str] = None
        #: The other `ValidatorAction`s` that this one depends on. If any errors occur in an action that this one depends on, this action will not be processed.

        self.__js_function: Optional[str] = None
        #: An optional field to contain the name to be used if JavaScript is generated.

        self.__validator_class: Optional[object] = None  
        #: Loaded class/module

    # ------------ Setters / Getters ------------

    @property
    def name(self) -> str:
        """Returns the name fo the validation.
        
        Returns: 
            name (str)
        """
        return self.__name

    @name.setter
    def name(self, value):
        """Sets the name of the validation."""
        self.__name = value

    @property
    def class_name(self) -> str:
        """Returns the class name of the class containing
        the validation method.

        Returns:
            class_name (str)
        """
        return self.__class_name

    @class_name.setter
    def class_name(self, value):
        """Sets the class name."""
        self.__class_name = value

    @property
    def method(self) -> str:
        """Returns the method name.

        Returns:
            method_name (str)
        """
        return self.__method

    @method.setter
    def method(self, value):
        """Sets the method name."""
        self.__method = value

    @property
    def depends(self) -> str:
        """Gets the other `ValidatorAction`s` that this one depends on. 

        Returns:
            depends (str)
        """
        return self.__depends

    @depends.setter
    def depends(self, value):
        """Sets the other `ValidatorAction`s` that this one depends on. """
        self.__depends = value

    def setJavascript(self, js_function) -> Optional[str]:
        """Sets the  field to contain the name to be used if JavaScript is generated.

        Args:
            js_function (str): the name to be used if JavaScript is generated
        """
        self.__js_function = js_function

    def getJavascript(self):
        """Gets the name to be used if javascript is generated."""
        return self.__js_function

    # ------------ Initialization ------------

    def init(self):
        """Dynamically load the validator class/module."""
        if not self.__class_name:
            raise ValueError("class_name must be set before init()")

        try:
            module_name, class_name = self.__class_name.rsplit(".", 1)
            module = importlib.import_module(module_name)
            self.__validator_class = getattr(module, class_name)
        except: 
            raise Exception(f"{self.__class_name} can't be imported. ")

    # ------------ Execution ------------

    def execute_validation_method(self, validator, params):
        """Executes the validation method.

        Args:
            validator: Validator instance (context).
            params: Validation parameters.

        Returns:
            Result of the validation (e.g., True/False).
        """
        if self.__validator_class is None:
            raise Exception("Validator class not initialized. Call init() first.")

        instance = (
            self.__validator_class() if callable(self.__validator_class) else self.__validator_class
        )

        method = getattr(instance, self.__method)
        return method(validator, params)

    # ------------ Dependency Parsing ------------

    def get_dependencies(self) -> List[str]:
        """Returns dependencies as a list."""
        if self.__depends:
            return [dep.strip() for dep in self.__depends.split(",")]
        return []

    def __str__(self):
        return (
            f"ValidatorAction(name={self.__name}, class_name={self.__class_name}, "
            f"method={self.__method}, depends={self.__depends})"
        )