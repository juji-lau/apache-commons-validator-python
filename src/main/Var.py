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

import copy
from typing import Final

class Var:
    JSTYPE_INT: Final[str] = "int"
    JSTYPE_STRING: Final[str] = "string"
    JSTYPE_REGEXP: Final[str] = "regexp"

    def __init__(self, name=None, value=None, js_type=None):
        """
        Initialize a Var instance.
        
        Args:
            name (str, optional): The variable's name.
            value (str, optional): The variable's value.
            js_type (str, optional): The variable's JavaScript type.
        """
        self._name: str = name          # The name of the variable.
        self._value: str = value        # The key or value of the variable.
        self._js_type: str = js_type    # Optional JavaScript type.
        self._resource: bool = False    # Whether the variable is a resource (default: False).
        self._bundle: str = None        # The bundle name (used when resource is True).
        self.serializable = True
        self.cloneable = True

    def clone(self):
        """
        Create and return a shallow copy of this Var instance.
        
        Returns:
            Var: A clone of the current instance.
        """
        return copy.deepcopy(self)

    @property
    def name(self):
        """Get or set the name of the variable."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def value(self):
        """Get the value of the variable."""
        return self._value

    @value.setter
    def value(self, value):
        """Set the value of the variable."""
        self._value = value

    @property
    def js_type(self):
        """Get the JavaScript type of the variable."""
        return self._js_type

    @js_type.setter
    def js_type(self, js_type):
        """Set the JavaScript type of the variable."""
        self._js_type = js_type

    @property
    def resource(self):
        """Indicates whether the value is a resource (True) or a literal value (False)."""
        return self._resource

    @resource.setter
    def resource(self, resource):
        """Set the JavaScript type of the variable."""
        self._resource = resource

    @property
    def bundle(self):
        """Get the resource bundle name for the variable (used when resource is True)."""
        return self._bundle

    @bundle.setter
    def bundle(self, bundle):
        """Set the resource bundle name for the variable (used when resource is True)."""
        self._bundle = bundle

    def __str__(self):
        """
        Return a string representation of the Var instance.
        
        Returns:
            str: A string that shows the variable's attributes.
        """
        parts = [
            f"Var: name={self._name}",
            f"  value={self._value}",
            f"  resource={self._resource}"
        ]
        if self._resource:
            parts.append(f"  bundle={self._bundle}")
        parts.append(f"  jsType={self._js_type}\n")
        return " ".join(parts)