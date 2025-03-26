"""
TODO: 
    - set up file description
    - setup logging and change functions to match
    - put constants into class
    - document class and class attributes
"""

import pytest
import logging
from typing import Final, Optional, Union

from src.main.routines.checkdigit.abstract_checkdigit import AbstractCheckDigit
from src.main.routines.checkdigit.checkdigit_exception import CheckDigitException

from src.main.routines.checkdigit.checkdigit import CheckDigit
from src.main.routines.checkdigit.ean13_checkdigit import EAN13CheckDigit
from src.main.routines.checkdigit.isbn10_checkdigit import ISBN10CheckDigit

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format= "%(levelname)s: %(message)s"
)
logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

# Constants
POSSIBLE_CHECK_DIGITS = "0123456789 ABCDEFHIJKLMNOPQRSTUVWXYZ\tabcdefghijklmnopqrstuvwxyz!@£$%^&*()_+"
# CHECKDIGIT
INVALID = ["12345678A"]                 # Invalid code
ZERO_SUM = "0000000000"                 # Code value which sums to zero

MISSING_MESSAGE = "Code is missing"     # Prefix for error messages


class AbstractCheckDigitTest:
    """
    TODO: insert documentation

    Attributes:
        log (logger): 
        checkdigit_len (int): The checkdigit routine being tested.  TODO: verify.
        routine (CheckDigit): The checkdigit routine being tested.
        valid (list[str]): List of valid code values, *including* the check digit.
            This is passed to: 
                CheckDigit.isValid(expects string including checkdigit) which is expected to return true 
                AbstractCheckDigitTest.createInvalidCodes() which mangles the last character to check that the result is now invalid.
                The truncated string is passed to CheckDigit.calculate(expects string without checkdigit).
                The result is compared with the last character
        invalid (list[str]): List of invalid code values. 
            These are currently passed to both:
                CheckDigit.calculate(expects a string without checkdigit) which is expected to throw an exception However that only applies if the string is syntactically incorrect.  
                CheckDigit.isValid(expects a string including checkdigit) which is expected to return False.
        zero_sum (str): Code value which sums to zero.
        missing_message(str): Prefix for error messages.
        serializable (bool): Indicates if the object is serializable (class attribute).
        clone (bool): Indicates if the object can be cloned (class attribute).
 
    Constants:
        POSSIBLE_CHECK_DIGITS (str): 

    """
    # _log:logging.Logger = logger.fa
    _checkdigit_len:Final[int] = 1
    _routine:CheckDigit
    _valid:list[str]
    _invalid:list[str] = ["12345678A"]
    _zero_sum:str = "0000000000"
    _missing_message:str = "Code is missing"

    # Attributes to manage serialization and cloning capabilities
    serializable = False   
    clone = False

    def setup_method(self) -> None:
        """ Sets up routine & valid codes."""
        pass

    def teardown_method(self) -> None:
        """Clears routine and valid codes."""
        self._valid = None
        self._routine = None


    # Internal helper methods
    def _checkdigit(self, code: str) -> str:
        """
        Returns the check digit (i.e. last character) for a code.

        Args:
            code (str): The code.

        Returns:
            The check digit.
        
        """
        if code is None or len(code) <= self._checkdigit_len:
            return ""
        return code[-self._checkdigit_len:]


    def _create_invalid_codes(self, codes:list[str]) -> list[str]:
        """
        Returns an array of codes with invalid check digits.
        
        Args:
            codes (list[str]): Codes with valid check digits.

        Returns:
            Codes with invalid check digits.
        """
        # create invalid check digit values
        invalid_codes = []
        for full_code in codes:
            code = self._remove_checkdigit(full_code)
            check = self._checkdigit(full_code)
            for j, curr in enumerate(POSSIBLE_CHECK_DIGITS):
                curr = POSSIBLE_CHECK_DIGITS[j:j+1]
                if curr != check:
                    invalid_codes.append(code + curr)
        return invalid_codes

    def _remove_checkdigit(self, code: str) -> str:
        """
        Returns a code with the Check Digit (i.e. last character) removed.
        
        Args:
            code (str): The code.
        
        Returns:
            The code without the check digit.
        """
        if code is None or len(code) <= self._checkdigit_len:
            return None
        return code[:len(code)-self._checkdigit_len]
    

    def test_calculate_invalid(self):
        """ Tests calculate() for invalid values."""
        # self._log.debug("test_calculate_invalid() for %s", self._routine.getclass.name)
        
        # test invalid values
        for i, code in enumerate(self._invalid):
            try:
                # self._log.debug(" %d Testing Invalid Check Digit, Code = [%s]", code)
                expected = self._checkdigit(code)
                code_with_no_checkdigit = self._remove_checkdigit(code)
                if code_with_no_checkdigit is None:
                    raise CheckDigitException(f"Invalid Code=[{code}]", ValueError())
                
                actual = self._routine.calculate(code_with_no_checkdigit)
                # If exception not thrown, check that the digit is incorrect instead
                assert actual != expected, f"Expected mismatch for {code} expected {expected} actual {actual}."

            except CheckDigitException as e:
                assert(str(e.value).startswith("Invalid "), f"Invalid Character[{i}]={str(e)}")
    

    # Test: calculate() returns the expected check digit for valid codes
    def test_calculate_valid(self):
        """ Tests calculate() for valid values."""
        # self._log.debug("test_calculate_valid() for %s", self._routine.getclass.name())
         
        # test valid values
        for i, valid_code in enumerate(self._valid):
            code = self._remove_checkdigit(valid_code)
            expected = self._checkdigit(valid_code)
            try:
                # self._log.debug(" %d Testing Valid Check Digit, Code=[%s] expected=[%s]", code, expected)
                assert expected == self._routine.calculate(code), f"valid['{i}']: {valid_code}"
            except Exception as e:
                # TODO: find a better way to force a fail message
                # Java: fail("valid[" + i + "]=" + valid[i] + " threw " + e);
                assert(True==False, f"valid{i}={valid_code} threw {str(e)}")
                # print(f"valid[{i}]={valid_code} threw {str(e)}")


    def test_is_valid_false(self):
        """Tests is_valid() for invalid values."""
        # self._log.debug("test_is_valid_false() for %s", self_routine.getclass.getname())

        # Test invalid code values
        for i, code in enumerate(self._invalid):
            # self._log.debug("   %d Testing Invalid Code=[%s]", i, code)
            assert not self._routine.is_valid(code), f"invalid[{i}]: {code}"

        # Test invalid check digit values
        invalid_checkdigits = self._create_invalid_codes(self._valid)
        for i, invalid_checkdigit in enumerate(invalid_checkdigits):
            # self._log.debug("   %d Testing Invalid Check Digit, Code=[%s]", i, invalid_checkdigit)
            assert not self._routine.is_valid(invalid_checkdigit), f"invalid[{i}]: {invalid_checkdigit}"
        
       
    def test_is_valid_true(self):
        """Tests is_valid() for valid values."""
        # self._log.debug("test_is_valid_true() for %s", self_routine.getclass.getname())

        # test valid values
        for i, code in enumerate(self._valid):
            # self._log.debug("   %d Testing Valid Code=[%s]", i, code)
            assert self._routine.is_valid(code), f"valid[{i}]: {code}"


    def test_missing_code(self):
        """Test missing code."""
        # is_valid() None
        assert self._routine.is_valid(None) == False, f"is_valid() None"

        # is_valid() zero length
        assert self._routine.is_valid("") == False, f"is_valid() Zero Length"

        # is_valid() length 1
        assert self._routine.is_valid("9") == False, f"is_valid() Length 1"

        # calculate() None
        with pytest.raises(Exception) as e:
            self._routine.calculate(None)
        assert str(e.value) == self._missing_message, "calcualte() Null"

        # calculate() zero length
        with pytest.raises(Exception) as e:
            self._routine.calculate("")
        assert str(e.value) == self._missing_message, f"calculate() Zero Length"


    def test_zero_sum(self):
        """Test zero sum"""
        assert not self._routine.is_valid(self._zero_sum), "is_valid() Zero Sum"
        with pytest.raises(Exception) as e:
            self._routine.calculate(self._zero_sum)
        assert str(e.value) == "Invalid code, sum is zero", "is_valid() Zero Sum"



    # # Test: serialization (using pickle)
    # def test_serialization(self):
    #     # Assume that the routine is pickle-serializable.
    #     try:
    #         serialized = pickle.dumps(self.routine)
    #         deserialized = pickle.loads(serialized)
    #         assert deserialized is not None
    #     except Exception as e:
    #         pytest.fail(f"{self.routine.__class__.__name__} error during serialization/deserialization: {e}")