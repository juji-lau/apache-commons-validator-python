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


class ValidatorException(Exception):
    """The base exception for the Validator Framework.  All other
    `Exception`s thrown during calls to `Validator.validate()` are considered errors.
    
    Taken from org.apache.commons.validator.ValidatorException;
    """
    serializable = True  #: is the class serializable
    cloneable = False #: is the class cloneable

    def __init__(self, message=None):
        """ValidatorException.

        Args:
            message (str, optional): message for ValidatorException to contain. Defaults to None.
        """
        super().__init__(message)