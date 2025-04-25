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
import logging
import importlib
from types import ModuleType
from typing import Optional, Any, Final, Type, Callable, List, Dict


class ValidatorAction:
     """
     Contains the information to dynamically create and run a validation method. 
     This is the class representation of a pluggable validator that can be
     defined in an xml file with the <validator> element. 

     Note: the original implementation was assumed to be thread safe. I can't 
     make the same guarantee here. 
     """
     pass
     # def __init__(self):

     #      self.__log: Optional[logging.Logger] = logging.getLogger(__name__) 
     #      #: Logger

     #      self.__name: Optional[str] = None
     #      #: The name of the validation

     #      self.__class_name: Optional[str] = None
     #      #: The full class name of the class containing the validation method associated with this action.

     #      self.__validation_class: Optional[Type] = None
     #      #: The Class object loaded from the class name. 

     #      self.__method: str = None
     #      #: the full method name of the validation to be performed. (method should be thread safe)

     #      self.__validation_method: Optional[Callable[...,Any]] = None
     #      #: The method object loaded from the method name

     #      self.__method_params: List[str] = None
     #      """
     #      The method signature of the validation method. This should be a comma-delimited list of the full class names of each parameter in the correct order that the method takes.

     #      object is reserved for the JavaBean that is being validated. The `ValidatorAction` and `Field` that
     #      are associated with a field's validation will automatically be populated if they are specified in the method signature.
     #      """

     #      self.__parameter_classes: Optional[List[type]] = None
     #      #: The Class objects for each entry in methodParameterList.

     #      self.__depends: Optional[str] = None
     #      #: The other ValidatorAction's that this one depends on. If any errors occur in an action that this one depends on, this action will not be processed.

     #      self.__msg: Optional[str] = None
     #      #: The default error message associated with this action.

     #      self.__js_function_name: Optional[str] = None
     #      #: An optional field to contain the name to be used if JavaScript is generated. 

     #      self.__js_function: Optional[str] = None
     #      #: An optional field to contain the class path to be used to retrieve the JavaScript function.

     #      self.__javascript: Optional[str] = None
     #      #: An optional field to containing a JavaScript representation of the Java method associated with this action.

     #      self.__instance: Optional[Any] = None
     #      #: If the Java method matching the correct signature isn't static, the instance is stored in the action. This assumes the method is thread safe.

     #      self.__dependency_list: Final[List[str]] = []
     #      #:  An internal List representation of the other ValidatorActions this one depends on (if any). This List gets updated whenever setDepends() gets called. This is synchronized so a call to setDepends() (which clears the List) won't interfere with a call to isDependency().

     #      self.__method_parameter_list: Final[List[str]] = []
     #      #: An internal List representation of all the validation method's parameters defined in the methodParams String.

     # def execute_validation_method(self, field: Field, params: Dict[str, object], results: ValidatorResults, pos: int) -> bool | ValidatorException:
     #      """
     #      Dynamically runs the validation method for this validator and returns true if the data is valid. 
          
     #      Args:
     #           field (Field)
     #           params (Dict[str, object]) - a dict of class names to parameter values
     #           results (ValidatorResults)
     #           pos (int) - the index of the list property to validate if it's indexed

     #      Returns:
     #           True if the data is valid. Throws ValidatorException.
     #      """
     #      raise NotImplementedError
     
     # def load_validation_class():
     #      raise NotImplementedError
     
     # def load_validation_method(): 
     #      raise NotImplementedError
     
     # def get_parameter_values():
     #      raise NotImplementedError
     
     # def is_valid(): 
     #      raise NotImplementedError
     
     # def handle_indexed_field(): 
     #      raise NotImplementedError
     
     # def is_dependency(): 
     #      raise NotImplementedError
     
