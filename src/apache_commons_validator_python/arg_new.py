"""Licensed to the Apache Software Foundation (ASF) under one or more contributor
license agreements.  See the NOTICE file distributed with this work for additional
information regarding copyright ownership. The ASF licenses this file to You under the
Apache License, Version 2.0 (the "License"); you may not use this file except in
compliance with the License.  You may obtain a copy of the License at.

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Optional


class Arg:
    """A default argument or an argument for a specific validator definition (ex:
    required) can be stored to pass into a message as parameters. This can be used in a
    pluggable validator for constructing locale sensitive messages by using
    `MessageFormat` or an equivalent class.  The resource field can be used to determine
    if the value stored in the argument is a value to be retrieved from a locale
    sensitive message retrieval system like ``java.util.PropertyResourceBundle``. The
    resource field defaults to 'true'.

    Instances of this class are configured with an <arg> xml element.

    Taken from apache.commons.validator.Arg;

    Attributes:
        serializable (bool): Indicates if the object is serializable.
        cloneable (bool): Indicates if the object can be cloned.
        bundle (str): The resource bundle name that this Arg's `key` should be resolved in (optional).
        key (str): The key or value of the argument.
        name (str): The name dependency that this argument goes with (optional).
        position (int): This argument's position in the message. Set position=0 to make a replacement in this string: "some msg {0}". @since 1.1
        resource(bool): Whether or not the key is a message resource (optional). Defaults to True. If it is 'true', the value will try to be resolved as a message resource.
    """

    serializable = True
    #: class is serializable

    cloneable = True
    #: class is cloneable

    def __init__(self):
        """Constructor for Arg, a default argument or an argument for a specific validator definition.
        """
        self._bundle: Optional[str] = None
        #: The resource bundle name that this Arg's `key` should beresolved in (optional).

        self._key: Optional[str] = None
        #: The key or value of the argument.

        self._name: Optional[str] = None
        #: The name dependency that this argument goes with (optional).

        self._position: int = -1
        #: This argument's position in the message. Set position=0 to make a replacement in this string: "some msg {0}". @since 1.1

        self._resource: bool = True
        #: Whether or not the key is a message resource (optional). Defaults to True. If it is 'true', the value will try to be resolved as a message resource.

    @property
    def bundle(self) -> Optional[str]:
        """
        Get the resource bundle name.

        Returns: 
            bundle (str)
        """
        return self._bundle

    @bundle.setter
    def bundle(self, value) -> None:
        """Sets the resource bundle name."""
        self._bundle = value

    @property
    def key(self) -> Optional[str]:
        """
        Gets the key/value.
        
        Returns:
            key (str)
        """
        return self._key

    @key.setter
    def key(self, value) -> None:
        """Sets the key/value."""
        self._key = value

    @property
    def name(self) -> Optional[str]:
        """
        Gets the name of the dependency.
        
        Returns: 
            name (str)
        """
        return self._name

    @name.setter
    def name(self, value) -> None:
        """Sets the name of the dependency."""
        self._name = value

    @property
    def position(self) -> int:
        """
        Gets the replacement position.
        
        Returns: 
            position (int)
        """
        return self._position

    @position.setter
    def position(self, value) -> None:
        """Sets the replacement position."""
        self._position = value

    @property
    def resource(self) -> bool:
        """
        Tests whether or not the key is a resource key or literal value.
        
        Returns:
            resource (bool)
        """
        return self._resource

    @resource.setter
    def resource(self, value) -> None:
        """Sets whether or not the key is a resource."""
        self._resource = value

    def __str__(self):
        return f"Arg: name={self._name}  key={self._key}  position={self._position}  bundle={self._bundle}  resource={self._resource}\n"