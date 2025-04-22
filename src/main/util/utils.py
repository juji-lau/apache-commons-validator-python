
import copy
<<<<<<< Updated upstream
from placeholders import Var, Arg, Msg

class ValidatorUtils:
    def __init__(self):
        self.serializable = False
        self.cloneable = False

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
=======
from typing import Any, Dict

from src.main.var import Var
from src.main.arg import Arg
from src.main.msg import Msg

class ValidatorUtils:
    """
    Holds translation from apache.commons.validator.utils.ValidatorUtils class
    """
    serializable = False
    cloneable = False
    
    @classmethod
    def copy_map(cls, map_arg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Makes and returns a deep copy of a map if the values are Msg, Arg, or Var,
        and a shallow copy otherwise.
        Python's version of: org.apache.validator.util.ValidatorUtils.copyMap()

        Parameters:
          map: The input map to copy

        Returns:
          new_map: The copied map, where for each entry, a deepcopy is made if the value
          is an Arg, Var, or Msg, and a shallow copy otherwise.
        """
        new_map = {}
        deep_copy_types = (Var, Arg, Msg)
>>>>>>> Stashed changes

        for key, val in map_arg.items():
            if isinstance(val, deep_copy_types):
                new_map[key] = copy.deepcopy(val)
            else:
                new_map[key] = copy.copy(val)

<<<<<<< Updated upstream
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
=======
        return new_map

    @classmethod
    def get_value_as_string(cls, bean: Any, bean_property: str) -> str:
        """
        Returns the value from the bean property as a string.
        Python's version of: org.apache.validator.util.ValidatorUtils.getValueAsString()
>>>>>>> Stashed changes

        Parameters:
          bean: An instance of a class
          property: A field in bean

<<<<<<< Updated upstream
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
      
=======
        Returns:
          out_str:
          - "" If property is an empty list, a list of empty strings, or an empty Collection
          - The result of property.toStr()
          - None if there's an error.
        """
        try:
            attr = getattr(bean, bean_property, None)
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
    def replace(cls, value: str, key: str, replace_value: str) -> str:
        """
        Replaces a key part of value with replaceValue
        Python's version of: org.apache.validator.util.ValidatorUtils.replace()

        Parameters:
          value: The string to perform the replacement on
          key: The name of the constant
          replace_value: The value of hte constant

        Returns:
          modified_value: The modified value
        """
        return value.replace(key, replace_value)
>>>>>>> Stashed changes
