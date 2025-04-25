# holds translation from apache.commons.validator.utils.ValidatorUtils class
import copy
from typing import Callable, Optional, Union

from src.main.var import Var
from src.main.arg import Arg
from src.main.msg import Msg

# Generic utility functions
def integer_compare(a:int, b:int) -> int:
    """
    Compares a, and b.

    Args:
        a (int): The first value to compare
        b (int): The second value to compare

    Returns:
        0 if a == b.
        -1 if a < b. 
        1 if a > b.
    """
    if a == b:
        return 0
    elif a > b:
        return 1
    return -1

def to_lower(s:str) -> Optional[str]:
    """
    Returns s with all letters lowercased, and leading and trailing whitespaces removed.

    Args:
        s (str): The string to process
    
    Returns:
        s with the leading and trailing whitespaces removed, and all letters lowercased.
        None if s is an invalid argument.
    """
    try:
        return s.strip().strip('_').lower()
    except Exception as e:
        print(f"Invalid argument: {s} with error: {e}") 
        return None

# Utility functions for Validators
class ValidatorUtils:
    def __init__(self):
        self.serializable = False
        self.cloneable = False

    @classmethod
    def copy_map(map:dict[str, object]) -> dict[str, object]:
        """
        Makes and returns a deep copy of a map if the values are Msg, Arg, or Var, 
        and a shallow copy otherwise. 

        Args:
            map (dict[str, object]): The input map to copy
        
        Returns: 
            The copied map, where for each entry, a deepcopy is made if the value 
            is an Arg, Var, or Msg, and a shallow copy otherwise. 
        """
        new_map = {}
        deep_copy_types = (Var, Arg, Msg)

        for key, val in map.items():
            if isinstance(val, deep_copy_types):
                new_map[key] = copy.deepcopy(val)
            else:
                new_map[key] = copy.copy(val)

        return new_map

    @classmethod
    def get_value_as_string(bean : object, property : str) -> str:
        """
        Returns the value from the bean property as a string.
        
        Args:
            bean (object): An instance of a class
            property (str): A field in bean
        
        Returns:
            - "" If property is an empty list, a list of empty strings, or an empty Collection
            - The result of property.toStr()
            - None if there's an error.
        """
        try: 
            attr = getattr(bean, property, None)
            # Check for empty Collection
            if attr in (None, [], set(), {}):
                return ""

            # Check list of empty strings. 
            if isinstance(attr, list):
                if all(isinstance(item, str) and item == "" for item in attr):
                    return ""
            
            # Return the string representation
            return str(attr)
        
        except Exception as e:
            print(f"Failed to stringify the bean property: {e}")
            return None


    @classmethod
    def replace(value: str, key:str, replace_value:str) -> str:
        """
        Replaces a key part of value with replaceValue

        Args:
            value (str): The string to perform the replacement on
            key (str): The name of the constant
            replace_value (str): The value of hte constant

        Returns:
            The modified value.
        """
        return value.replace(key, replace_value)
      