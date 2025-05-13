import importlib
from typing import Optional

class ValidatorAction:
    def __init__(self):
        self.__name: Optional[str] = None
        self.__class_name: Optional[str] = None
        self.__method: Optional[str] = None
        self.__depends: Optional[str] = None
        self.__js_function: Optional[str] = None
        self.__validator_class: Optional[object] = None  # Loaded class/module

    # ------------ Setters / Getters ------------

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def class_name(self):
        return self.__class_name

    @class_name.setter
    def class_name(self, value):
        self.__class_name = value

    @property
    def method(self):
        return self.__method

    @method.setter
    def method(self, value):
        self.__method = value

    @property
    def depends(self):
        return self.__depends

    @depends.setter
    def depends(self, value):
        self.__depends = value

    def setJavascript(self, js_function):
        self.__js_function = js_function

    def getJavascript(self):
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

    def get_dependencies(self):
        """Returns dependencies as a list."""
        if self.__depends:
            return [dep.strip() for dep in self.__depends.split(",")]
        return []

    def __str__(self):
        return (
            f"ValidatorAction(name={self.__name}, class_name={self.__class_name}, "
            f"method={self.__method}, depends={self.__depends})"
        )