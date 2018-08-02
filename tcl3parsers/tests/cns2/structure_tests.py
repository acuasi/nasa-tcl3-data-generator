"""Provides tests for cns2.py values."""
import json
import unittest

# Include local testing constants, adds tcl3parsers to path
import constants

class TestValueTypes(unittest.TestCase):
    """Adds test cases for value type"""

    @classmethod
    def setUpClass(cls):
        generatedFile = open(constants.OUTFILE_NAME, "r")
        cls.cns2_data = json.load(generatedFile)

    def __matchException(self, key, exceptionMatch, actualData):
        return exceptionMatch == actualData

    def __checkExact(self, key, expectedData, actualData):
        self.assertEqual(actualData, expectedData)

    def __checkType(self, key, expectedType, actualData):
        actualType = type(actualData).__name__
        self.assertTrue(actualType == expectedType, "Expected type for "
                        + str(key) + ": " + str(expectedType) + ", actual type: "
                        + str(actualType))

    def __checkPattern(self, key, pattern, actualData):
        self.assertRegex(actualData, pattern)

    def __checkMinLength(self, key, minLength, actualData):
        self.assertTrue(len(actualData) >= minLength, "Min length mismatch for: "
                        + str(key) + ". expected: " + str(minLength)
                        + ", actual: " + str(actualData))

    def __checkMaxLength(self, key, maxLength, actualData):
        self.assertTrue(len(actualData) <= maxLength, "Max length mismatch for: "
                        + str(key) + ". expected: " + str(maxLength)
                        + ", actual: " + str(actualData))

    def __matchParameters(self, key, expectedParams, actualData):
        # If the exception case matches, then ignore testing the field
        if 'exception' in expectedParams:
            if self.__matchException(key, expectedParams['exception'], actualData):
                return
        if 'exact' in expectedParams:
            self.__checkExact(key, expectedParams['exact'], actualData)
        if 'type' in expectedParams:
            self.__checkType(key, expectedParams['type'], actualData)
        if 'pattern' in expectedParams:
            self.__checkPattern(key, expectedParams['pattern'], actualData)
        if 'minLength' in expectedParams:
            self.__checkMinLength(key, expectedParams['minLength'], actualData)
        if 'maxLength' in expectedParams:
            self.__checkMaxLength(key, expectedParams['maxLength'], actualData)
        if 'children' in expectedParams:
            # Checked that the parent structure matched spec, now recurse through children
            self.__testStructure(expectedParams['children'], actualData)

    # start with constants.CNS2_MOP and self.cns2_data, recurse
    def __testStructure(self, expectedData, actualData):
        # Base case - if the structure is empty or not the right type, return
        if not isinstance(expectedData, dict) or not isinstance(actualData, dict) or not expectedData or not actualData:
            return

        for key, value in expectedData.items():
            if isinstance(value, dict) and 'match' in value.keys():
                expectedParams = value['match']
                self.assertIn(key, actualData)
                self.__matchParameters(key, expectedParams, actualData[key])

            else:
                self.__testStructure(value, actualData[key])

    def test_structure(self):
        """Run all test cases comparing the outputted JSON file against the expected structure found in constants.py"""
        self.__testStructure(constants.CNS2_MOP, self.cns2_data)
