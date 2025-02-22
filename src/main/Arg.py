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
class Arg:
    def __init__(self):
        self._bundle = None  #The resource bundle name that this Arg's {@code key} should beresolved in (optional).
        self._key = None  #The key or value of the argument.
        self._name = None #The name dependency that this argument goes with (optional).
        self._position = -1 #This argument's position in the message. Set position=0 to make a replacement in this string: "some msg {0}". @since 1.1
        self.serializable = True #class is serializable
        self.clone = True #class is cloneable

    # Getter and setter for bundle
    @property  #define a method that acts as an attribute
    def bundle(self):
        return self._bundle

    @bundle.setter
    def bundle(self, value):
        self._bundle = value

    # Getter and setter for key
    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    # Getter and setter for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    # Getter and setter for position
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    # Getter and setter for resource
    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, value):
        self._resource = value

    # Python automatically calls this method to convert the object to a string
    def __str__(self):
        return f"Arg: name={self._name}  key={self._key}  position={self._position}  bundle={self._bundle}  resource={self._resource}"
 