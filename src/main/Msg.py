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
from typing import Final, Optional
import pickle

class Msg:
    """
    The Msg class represents a message that can be associated with a `Field` 
    and a pluggable validator. It allows customization of the message, 
    enabling alternative messages to be used instead of the default stored 
    in the `ValidatorAction`. Instances are configured with a <msg> XML element.
    """

    serializable: Final[bool] = True  # Indicates if the object can be serialized
    cloneable: Final[bool] = True  # Indicates if the object can be cloned
    _logger = logging.getLogger(__name__)  # Logger for the Msg class

    def __init__(self):
        # Initialize optional properties for the message
        self._bundle: Optional[str] = None  # Resource bundle name for localization (optional)
        self._key: Optional[str] = None  # Key for the message (optional)
        self._name: Optional[str] = None  # Dependency name (optional)
        self._resource: bool = True  # Whether the key is a resource (default is True)
        

    def clone(self) -> "Msg":
        """
        Creates and returns a deep copy of the current Msg instance using serialization.
        This method utilizes `pickle` to serialize and deserialize the object.
        """
        try:
            return pickle.loads(pickle.dumps(self))  # Serialize and deserialize to create a clone
        except Exception as e:
            # Raises an exception if cloning is not supported or fails
            raise UnsupportedOperationException(f"Clone not supported: {e}")

    @property
    def bundle(self) -> Optional[str]:
        """Gets the resource bundle name."""
        return self._bundle

    @bundle.setter
    def bundle(self, bundle: Optional[str]) -> None:
        """Sets the resource bundle name."""
        self._bundle = bundle

    @property
    def key(self) -> Optional[str]:
        """Gets the key value."""
        return self._key

    @key.setter
    def key(self, key: Optional[str]) -> None:
        """Sets the key value."""
        self._key = key

    @property
    def name(self) -> Optional[str]:
        """Gets the dependency name."""
        return self._name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        """Sets the dependency name."""
        self._name = name

    @property
    def resource(self) -> bool:
        """Tests whether the key is a resource key or a literal value."""
        return self._resource

    @resource.setter
    def resource(self, resource: bool) -> None:
        """Sets whether the key is a resource."""
        self._resource = resource

    def __str__(self) -> str:
        """
        Returns a string representation of the Msg instance showing its key properties.
        This helps with debugging and logging.
        """
        return f"Msg: name={self._name}  key={self._key}  resource={self._resource}  bundle={self._bundle}\n"


class UnsupportedOperationException(Exception):
    """Custom exception raised when an unsupported operation is attempted."""
    pass
