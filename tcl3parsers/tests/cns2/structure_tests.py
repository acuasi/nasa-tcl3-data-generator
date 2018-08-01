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

    def __checkType(self, key, value, actualData):
        expectedType = value['type']
        actualType = type(actualData).__name__
        self.assertTrue(actualType == expectedType, "Expected type for "
                        + str(key) + ": " + str(expectedType) + ", actual type: "
                        + str(actualType))

    def __checkPattern(self, key, value, actualData):
        self.assertRegex(actualData, value['pattern'], "Expected pattern for "
                         + str(key) + ": " + str(value['pattern'])
                         + ", doesn't match: " + str(actualData))

    def __checkMinLength(self, key, value, actualData):
        self.assertTrue(len(actualData) >= value['minLength'], "Min length mismatch for: "
                        + str(key) + ". expected: " + str(value['minLength'])
                        + ", actual: " + str(actualData))

    def __checkMaxLength(self, key, value, actualData):
        self.assertTrue(len(actualData) <= value['maxLength'], "Max length mismatch for: "
                        + str(key) + ". expected: " + str(value['minLength'])
                        + ", actual: " + str(actualData))

    # start with constants.CNS2_MOP and self.cns2_data, recurse
    def __testStructure(self, expectedData, actualData):
        if not isinstance(expectedData, dict) or not isinstance(actualData, dict) or not expectedData or not actualData:
            return
        for key, value in expectedData.items():
            if isinstance(value, dict) and 'match' in value.keys():
                matchParams = value['match']
                self.assertIn(key, actualData)
                if 'type' in matchParams:
                    self.__checkType(key, matchParams, actualData[key])
                if 'pattern' in matchParams:
                    self.__checkPattern(key, matchParams, actualData[key])
                if 'minLength' in matchParams:
                    self.__checkMinLength(key, matchParams, actualData[key])
                if 'maxLength' in matchParams:
                    self.__checkMaxLength(key, matchParams, actualData[key])
            else:
                self.__testStructure(value, actualData[key])

    def test_structure(self):
        self.__testStructure(constants.CNS2_MOP, self.cns2_data)
