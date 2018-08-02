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
        expectedType = expectedType.split("|")
        actualType = type(actualData).__name__
        self.assertIn(actualType, expectedType, str(key) + " from : " + self.parentKey)

    def __checkPattern(self, key, pattern, actualData):
        self.assertRegex(actualData, pattern)

    def __checkMinLength(self, key, minLength, actualData):
        self.assertLessEqual(minLength, len(actualData), "Minimum Length requirement not met for: " + str(key))

    def __checkMaxLength(self, key, maxLength, actualData):
        self.assertGreaterEqual(maxLength, len(actualData), "Maximum Length requirement not met for: " + str(key))

    def __checkMinimum(self, key, minimum, actualData):
        self.assertLessEqual(minimum, actualData)

    def __checkMaximum(self, key, maximum, actualData):
        self.assertGreaterEqual(maximum, actualData)

    def __testChildren(self, key, expectedChildren, actualData):
        # If there is a match immediately under the children, then this is an iterated match
        if 'match' in expectedChildren:
            for individualItem in actualData:
                self.__matchParameters(key, expectedChildren['match'], individualItem)
        else:
            self.__testStructure(expectedChildren, actualData, key)

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
        if 'maximum' in expectedParams:
            self.__checkMaximum(key, expectedParams['maximum'], actualData)
        if 'minimum' in expectedParams:
            self.__checkMinimum(key, expectedParams['minimum'], actualData)
        if 'children' in expectedParams:
            self.__testChildren(key, expectedParams['children'], actualData)

    # start with constants.CNS2_MOP and self.cns2_data, recurse
    def __testStructure(self, expectedData, actualData, parentKey=""):
        self.parentKey = parentKey
        # Base case - if the structure is empty or not the right type, return
        if not isinstance(expectedData, dict) or not isinstance(actualData, dict) or not expectedData or not actualData:
            return

        for key, value in expectedData.items():
            if isinstance(value, dict) and 'match' in value.keys():
                expectedParams = value['match']
                self.assertTrue(key in actualData, "Key not found in JSON: " + key)
                self.__matchParameters(key, expectedParams, actualData[key])

            else:
                self.assertTrue(key in actualData, "Key not found in JSON: " + key)
                self.__testStructure(value, actualData[key], "--TOP LEVEL JSON VAR--")
    def test_structure(self):
        """Run all test cases comparing the outputted JSON file against the expected structure found in constants.py"""
        self.__testStructure(constants.CNS2_MOP, self.cns2_data)
