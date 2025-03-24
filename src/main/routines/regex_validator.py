""" 
Module Name: regex_validator.py
Description: Translates apache.commons.validator.routines.RegexValidator.java
    Link: https://github.com/apache/commons-validator/blob/master/src/main/java/org/apache/commons/validator/routines/RegexValidator.java
    Paraphrased from apache.commons.validator.routines.RegexValidator:
    
    Regular Expression validation (using Python's built-in `re` module).
    
    Constructs the validator either for a single regular expression or a set (list) of regular expressions. 
    By default, validation is *case sensitive* but constructors are provided to allow *case-insensitive* validation. 
    
    Example:
        To create a validator which does case in-sensitive validation for a set of regular expressions:
            ```
            regexs = "some_str"
            validator = RegexValidator(regexs, case_sensitive=False)
            ```

        Validate returning a boolean (`True` or `False`):
            ```
            valid = validator.is_valid(some_value)
            ```

        Validate returning an aggregated String of the matched groups:
            ```
            result = validator.validate(some_value)
            ```

        Validate and return the matched groups as a list of strings:
            ```
            result = validator.match(some_value)
            ```
    
    Note:
        Patterns are matched against the entire input.

    Thread Safety:
        Compiled regex patterns are cached and can be used in multi-threaded environments safely.

Author: Juji Lau
License (Taken from apache.commons.validator.routines.RegexValidator):
    Licensed to the Apache Software Foundation (ASF) under one or more
    contributor license agreements. See the NOTICE file distributed with
    this work for additional information regarding copyright ownership.
    The ASF licenses this file to You under the Apache License, Version 2.0
    (the "License"); you may not use this file except in compliance with
    the License. You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
Changes:
    - Java uses the package `Pattern` for regular expressions. This Python file uses the `re` package.
    - Removed:
        - `CASE_SENSITIVE` 
            It was private constant (so no outside code calling). 
            Instead, we passed `case_sensitive` as an argument to __init__(), setting it to True by default.
        - `toCompileFlags()` 
            We only have one flag to keep track of (`re.IGNORECASE`).
    - Substitutions (Java -> Python):
        `java.util.regex`           ->  `re`                    Regex package
        `regex.compile()`           ->  `re.compile()`          Compiles a Pattern
        `regex.Pattern`             ->  `re.Pattern`
        `Pattern.CASE_INSENSITIVE`  ->  `re.INGORECASE`         Flag to ignore case when pattern matching.
        `Pattern.pattern`           ->  `Pattern.pattern`       Field that represents the pattern regex as a string.
        `Pattern.matcher(value).matches()`  ->  `Pattern.fullmatch(value)`        Matches the entire value against the pattern.   
            Java: 
                `Pattern.matcher(value)`    Creates a `Matcher` object that matches the entire value against the pattern.
                `matches()`                 Returns True iff the entire value matches the regex pattern. 
            Python: 
                `Pattern.fullmatch()`       Creates a `Match` object that matches the entire value against the pattern. None if there is no match.
        `regex.Matcher`             ->      `re.Match`          Object created by calling method(s) on `Pattern`.
        `Matcher.groups()`          ->      `Match.groups()`    List of all the matches in the string to the pattern regex.
        `java.lang.Object.clone()`  ->      `copy.copy()`       For shallow copies
"""

from re import Pattern, compile, IGNORECASE
from copy import copy
from typing import Optional, Union, Final

class RegexValidator:
    """
    A regular expression validator using Python's `re` module.

    Supports validation against one or multiple regex patterns, with an option for case insensitivity.

    Attributes:
        patterns (list[Pattern]): Compiled regex patterns.
        serializable (bool): Indicates if the object is serializable.
        cloneable (bool): Indicates if the object can be cloned.
    """
    # Attributes to manage serialization and cloning capabilities
    serializable = True    # class is serializable
    clone = False          # class is not cloneable

    def __init__(self, regexs:Union[str, list[str]], case_sensitive:bool = True):
        """
        Initializes a RegexValidator with one or more regular expressions.

        Args:
            regexs (Union[str, list[str]]): A regex pattern or a list of patterns.
            case_sensitive (bool): If `False`, enables case-insensitive matching (default: `True`).

        Raises:
            ValueError: If `regexs` is empty, `None`, or not a valid type.
        """
        self.__patterns = []
        
        # Get the correct compile() flags.
        if case_sensitive == True:
            flags = 0
        else:
            flags = IGNORECASE
        
        # If regexs is None or empty
        if regexs is None or regexs == "" or (isinstance(regexs, list) and len(regexs) == 0):
            raise ValueError("Regular expressions are missing.")
        
        # If regex is the wrong type
        if not isinstance(regexs, (str, list)):
            raise ValueError("Regexs must be a String or a list of Strings.")

        try:
            # Regexs is a string
            if isinstance(regexs, str):
                self.__patterns.append(compile(regexs, flags))
            # Regexs is a list
            else:
                for regex in regexs:
                    if regex is None or regex == "":
                        raise ValueError("Regular expressions are missing.")
                    self.__patterns.append(compile(regex, flags))
        except Exception as e:
            raise ValueError(f"Failed to compile {regexs} with error message: {e}")        
       

    @property
    def patterns(self) -> list[Pattern]:
        """
        Returns a shallow copy of the class attribute patterns.

        Note: 
        Since we return a shallow copy of self.__patterns, when we referecne self.__patterns
        in this class, we use self.__patterns to avoid making a new shallow copy at each reference.
        """
        return copy(self.__patterns)
    

    def is_valid(self, value:str) -> bool:
        """
        Validates a value against the set of regular expressions.

        Args:
            value (str): The value to validate.
  
        Returns: 
            `True` if any pattern fully matches `value`, else `False`.
        """
        if value is None:
            return False
        
        for pattern in self.__patterns:
            # Python's re.Pattern.fullmatch() matches the entire `value` against the pattern, 
            # and returns the `re.Match` object, or None if the value doesn't match.
            match = pattern.fullmatch(value)
            if match is not None:             # No match for this pattern
                return True
        return False
    
    def match(self, value:str) -> Optional[list[str]]:
        """
        Matches the input value against the regex patterns and returns matched groups.

        Args:
            value (str): The input string to validate.

        Returns:
            list[str] | None: A list of matched groups if valid; otherwise `None`.
        """
        if value is None:
            return None
        
        for pattern in self.__patterns:
            matches = pattern.fullmatch(value)
            if matches is not None:
                return list(matches.groups())
        return None

    def validate(self, value:str) -> Optional[str]:
        """
        Matches the input value and returns the concatenated matched groups.

        Args:
            value (str): The input string to validate.

        Returns:
            str | None: Concatenated matched groups if valid; otherwise `None`.
        """
        if value is None:
            return None

        for pattern in self.__patterns:
            matches = pattern.fullmatch(value)
            if matches is not None:
                groups = matches.groups()
                return "".join(list(groups))
        return None

    def __str__(self) -> str:
        """
        Returns a String representation of this validator.
        """
        output_str = "RegexValidator{"
        for i, pattern in enumerate(self.__patterns):
            if i > 0:
                output_str += ","
            output_str += pattern.pattern
        output_str += "}"
        return output_str