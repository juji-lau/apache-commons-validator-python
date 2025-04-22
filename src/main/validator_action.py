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


     def __init__(self):

          self.__log: Optional[logging.Logger] = logging.getLogger(__name__) 
          #: Logger

          self.__name: Optional[str] = None
          #: The name of the validation

          self.__class_name: Optional[str] = None
          #: the full class name of the class containing the validation method associated with this action.

          self.__method: str = None
          #: the full method name of the validation to be performed. (method should be thread safe)

          self.__method_params: List[str] = None
          """
          The method signature of the validation method. This should be a comma-delimited list of the full class names of each parameter in the correct order that the method takes.

          object is reserved for the JavaBean that is being validated. The `ValidatorAction` and `Field` that
          are associated with a field's validation will automatically be populated if they are specified in the method signature.
          """

          self.__instance: Optional[Any] = None
          #: 
          
          self.__validation_method: Optional[Callable[...,Any]] = None
          #: The method object loaded from the method name

          self.__validation_class: Optional[Type] = None
          #: The Class object loaded from the class name. 

          self.__depends: Optional[str] = None
          #: 


     
          