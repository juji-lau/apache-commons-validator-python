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

from main import GenericTypeValidator, Validator, ValidatorException, GenericValidator
from src.main.util.utils import ValidatorUtils
from typing import Final


class GenericValidatorImpl:
    # Constants for different field validation conditions
    FIELD_TEST_NULL: Final[str] = "NULL"
    FIELD_TEST_NOTNULL: Final[str] = "NOTNULL"
    FIELD_TEST_EQUAL: Final[str] = "EQUAL"

    @staticmethod
    def is_string_or_null(o: object) -> bool:
        '''
        Checks if the input object is either None or a string.
        '''
        if o is None:
            return True  # Currently, this condition isn't covered by tests
        return isinstance(o, str)

    @staticmethod
    def validate_byte(bean: object, field) -> bool:
        '''
        Validates if the field value can be interpreted as a byte.
        '''
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericValidator.is_byte(value)

    @staticmethod
    def validate_double(bean: object, field) -> bool:
        '''
        Validates if the field value can be interpreted as a double.
        '''
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericValidator.is_double(value)

    @staticmethod
    def validate_email(bean: object, field) -> bool:
        '''
        Validates if the field value is a valid email address.
        '''
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericValidator.is_email(value)

    @staticmethod
    def validate_float(bean: object, field) -> bool:
        '''
        Validates if the field value can be interpreted as a float.
        '''
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericValidator.is_float(value)

    @staticmethod
    def validate_int(bean: object, field) -> bool:
        '''
        Validates if the field value can be interpreted as an integer.
        '''
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericValidator.is_int(value)

    @staticmethod
    def validate_long(bean: object, field) -> bool:
        '''
        Validates if the field value can be interpreted as a long integer.
        '''
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericValidator.is_long(value)

    @staticmethod
    def validate_positive(bean: object, field) -> bool:
        '''
        Checks if the field value is a positive integer.
        '''
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericTypeValidator.format_int(value) > 0

    @staticmethod
    def validate_raise_exception(bean: object, field) -> bool:
        '''
        Triggers exceptions based on the field value ("RUNTIME", "CHECKED", or generic exception).
        '''
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())

        if value == "RUNTIME":
            raise RuntimeError("RUNTIME-EXCEPTION")
        if value == "CHECKED":
            raise Exception("CHECKED-EXCEPTION")
        raise ValidatorException("VALIDATOR-EXCEPTION")

    @staticmethod
    def validate_required(bean: object, field) -> bool:
        '''
        Validates if the field is required (i.e., not blank or null).
        '''
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return not GenericValidator.is_blank_or_null(value)

    @staticmethod
    def validate_required_if(bean: object, field, validator) -> bool:
        '''
        Validates if the field is required based on the value of other fields.
        '''
        form = validator.get_parameter_value(Validator.BEAN_PARAM)
        value = None
        required = False
        
        if GenericValidatorImpl.is_string_or_null(bean):
            value = str(bean)
        else:
            value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        
        i = 0
        field_join = "AND"
        
        if not GenericValidator.is_blank_or_null(field.get_var_value("fieldJoin")):
            field_join = field.get_var_value("fieldJoin")
        
        if field_join.lower() == "and":
            required = True
        
        # Checks dependency conditions for required validation
        while not GenericValidator.is_blank_or_null(field.get_var_value(f"field[{i}]")):
            depend_prop = field.get_var_value(f"field[{i}]")
            depend_test = field.get_var_value(f"fieldTest[{i}]")
            depend_test_value = field.get_var_value(f"fieldValue[{i}]")
            depend_indexed = field.get_var_value(f"fieldIndexed[{i}]")
            if depend_indexed is None:
                depend_indexed = "false"
            
            this_required = False
            if field.is_indexed() and depend_indexed.lower() == "true":
                key = field.get_key()
                if "[" in key and "]" in key:
                    ind = key[:key.index(".") + 1]
                    depend_prop = ind + depend_prop
            
            depend_val = ValidatorUtils.get_value_as_string(form, depend_prop)
            
            # Perform different tests based on the dependency test type
            if depend_test == GenericValidatorImpl.FIELD_TEST_NULL:
                this_required = depend_val is None or depend_val == ""
            elif depend_test == GenericValidatorImpl.FIELD_TEST_NOTNULL:
                this_required = depend_val is not None and depend_val != ""
            elif depend_test == GenericValidatorImpl.FIELD_TEST_EQUAL:
                this_required = depend_test_value.lower() == depend_val.lower()
            
            # Combine results based on "AND" or "OR" field join
            if field_join.lower() == "and":
                required = required and this_required
            else:
                required = required or this_required
            i += 1
        
        # Final check for required field
        if required:
            return value is not None and value != ""
        return True

    @staticmethod
    def validate_short(bean: object, field) -> bool:
        '''
        Validates if the field value can be interpreted as a short integer.
        '''
        value = ValidatorUtils.get_value_as_string(bean, field.get_property())
        return GenericValidator.is_short(value)
