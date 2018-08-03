import json
import unittest

class StructureTestController(unittest.TestCase):
    """Adds test cases for value type"""

    def __matchException(self, key, exceptionMatch, actualData):
        return exceptionMatch == actualData

    def __checkExact(self, key, expectedData, actualData):
        self.assertEqual(actualData, expectedData)

    def __checkType(self, key, expectedType, actualData):
        expectedType = expectedType.split("|")
        actualType = type(actualData).__name__
        self.assertIn(actualType, expectedType, str(key) + " from : " + str(self.parentKey))

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
        # If 'match' is found within expectedChildren, then the actualData is iterable and whatever is nested further must match ALL items
        # Example actualData: [{lat:0,lon:0}, {lat:0,lon:0}] or [0,1,2,3]
        # Example expectedChildren: {'match': 'children': {'lat': 'match':{...}, 'lon': 'match':{...}}}
        if "match" in expectedChildren:
            for individualItem in actualData:
                self.__matchParameters(key, expectedChildren['match'], individualItem)
        # If 'match' is not found, then this must mean that actualData is another JSON/dict that are "children" values
        # This is the case when there is a list of dictionaries. This else case would run for an individual dictionary and recurse through runStructureTest
        else:
            self.runStructureTest(expectedChildren, actualData, key)

    def __matchParameters(self, key, expectedParams, actualData):
        # If the exception case matches, then ignore testing the field
        for expectedParam in expectedParams:
            if expectedParam == 'exception':
                if self.__matchException(key, expectedParams[expectedParam], actualData):
                    print("Exception matched for:", key, " with value:", actualData)
                    return
            elif expectedParam == 'exact':
                self.__checkExact(key, expectedParams[expectedParam], actualData)
            elif expectedParam == 'type':
                self.__checkType(key, expectedParams[expectedParam], actualData)
            elif expectedParam == 'pattern':
                self.__checkPattern(key, expectedParams[expectedParam], actualData)
            elif expectedParam == 'minLength':
                self.__checkMinLength(key, expectedParams[expectedParam], actualData)
            elif expectedParam == 'maxLength':
                self.__checkMaxLength(key, expectedParams[expectedParam], actualData)
            elif expectedParam == 'maximum':
                self.__checkMaximum(key, expectedParams[expectedParam], actualData)
            elif expectedParam == 'minimum':
                self.__checkMinimum(key, expectedParams[expectedParam], actualData)
            elif expectedParam == 'children':
                self.__testChildren(key, expectedParams[expectedParam], actualData)
            else:
                self.assertTrue(False, "No expected parameters for " + key + " were tested. Malformed testing JSON.")

    # start with constants.CNS2_MOP and self.cns2_data, recurse
    def runStructureTest(self, expectedData, actualData, parentKey=""):
        """Iterates through every key in outputted JSON and compares it to parameters set in a testing JSON"""
        self.parentKey = parentKey
        # Base case - if the structure is empty or not the right type, return
        if not isinstance(expectedData, dict) or not hasattr(actualData, '__iter__') or not expectedData or not actualData:
            return

        for key, value in expectedData.items():
            if isinstance(value, dict) and 'match' in value.keys():
                expectedParams = value['match']
                self.assertTrue(key in actualData, "Key not found in JSON: " + key + " (parentKey: " + str(self.parentKey) + ")")
                self.__matchParameters(key, expectedParams, actualData[key])

            else:
                self.assertTrue(key in actualData, "Key not found in JSON: " + key + " (parentKey: " + str(self.parentKey) + ")")
                self.runStructureTest(value, actualData[key], "Last Key: " + key)
