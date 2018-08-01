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
        if 'type' in value['match']:
            self.assertIsInstance(actualData, value['type'])

    def __checkPattern(self, key, value, actualData):
        if 'pattern' in value['match']:
            self.assertRegex(actualData, value['pattern'])

    def __checkMinLength(self, key, value, actualData):
        if 'minLength' in value['match']:
            self.assertTrue(len(actualData) is value['minLength'])

    def __checkMaxLength(self, key, value, actualData):
        if 'maxLength' in value['match']:
            self.assertTrue(len(actualData) is value['maxLength'])

    # start with constants.CNS2_MOP and self.cns2_data, recurse
    def __testStructure(self, arr, actualData):
        for key, value in arr:
            if isinstance(value, 'dict') and 'match' in value.keys:
                self.__checkType(key, value, actualData[key])
                self.__checkPattern(key, value, actualData[key])
                self.__checkMinLength(key, value, actualData[key])
                self.__checkMaxLength(key, value, actualData[key])
            else:
                self.__testStructure(value, actualData[key])

    def test_structure(self):
        self.__testStructure(constants.CNS2_MOP, self.cns2_data)

    def test_fail(self):
        self.assertTrue(False)
