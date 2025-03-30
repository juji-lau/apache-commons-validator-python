"""
Module Name: re.y
Description: 
    Provides a wrapper class for python's `re` module, by overriding some of the methods so their
    specifications more closely match the corresponding methods in Java's `Pattern` package.

    Used internally in `src/main/routines/regex_validator.py`, and dependencies.

Author: Juji Lau

Substitutions:
    Java uses the package `Pattern` for regular expressions. 
    This Python file uses the `re` package.
      
    Substitutions (Java -> Python):
        `java.util.regex`           ->  `re`                    Regex package
        `Pattern.compile()`           ->  `re.compile()`          Compiles a Pattern
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
import re
from re import Pattern, compile, IGNORECASE
from typing import Optional, override

class Regex:
    """
    A partial wrapper class for Python's `re` module, emulating specific functionalities in Java's `Pattern` package.

    This class includes only the methods and attributes pertinent to the translation project, 
    omitting other functionalities of Java's `Pattern` class.

    Attributes:
        CASE_INSENSITIVE (int): Flag to perform case-insensitive matching, equivalent to `re.IGNORECASE`.
    """
    CASE_INSENSITIVE:int = IGNORECASE

    @classmethod
    def pattern_matches(cls, pattern: Pattern, string: str) -> bool:
        """
        Determines if the entire string matches the given pattern.

        This method serves as a substitute for Java's `Pattern.matcher().matches()`,
        providing equivalent functionality in Python.

        Args:
            pattern (Pattern): The compiled regular expression pattern.
            string (str): The string to be matched against the pattern.

        Returns:
            bool: True if the entire string matches the pattern; False otherwise.
        """
        return pattern.fullmatch(string) is not None
    
    @staticmethod
    def compile(pattern_str: str, flags: Optional[int] = 0) -> Pattern:
        """
        Compile a regular expression pattern into a Pattern object.
        This method emulates Java's `Pattern.compile()` method.

        Args:
            pattern (str): The regular expression pattern to compile.
            flags (int, optional): Flags to modify the regular expression's behavior. Defaults to 0.

        Returns:
            Pattern: The compiled regular expression pattern object.
        """
        return re.compile(pattern_str, flags)
    
    

