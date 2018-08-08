import json
import unittest

class StructureTestController(unittest.TestCase):
    """Adds test cases for matching the SwaggerHub spec"""
    def __init__(self, *args, **kwargs):
        super(StructureTestController, self).__init__(*args, **kwargs)
        self.exceptionsMatched = {}
        self.fixedData = False

    def printExceptionsMatched(self):
        """prints all allowed exceptions that were matched"""
        print("\n\n")
        for exceptionMatched, exceptionInfo in self.exceptionsMatched.items():
            print("EXCEPTION MATCHED:", exceptionMatched, "was matched", exceptionInfo["exceptionCount"], "times with the values:", exceptionInfo["exceptionValues"])
            if exceptionInfo["fix"]:
                print("\tEXCEPTION FIXED TO:", exceptionInfo["fix"])
        print("\n")

    def __matchException(self, key, exceptionMatchList, actualData, fix=""):
        if not isinstance(exceptionMatchList, list):
            exceptionMatchList = [exceptionMatchList]

        exceptionMatched = False
        for exceptionMatch in exceptionMatchList:
            try:
                exceptionMatched = str(actualData) == exceptionMatch or actualData == exceptionMatch or type(actualData).__name__ == exceptionMatch
            except ValueError:
                exceptionMatched = actualData == exceptionMatch
            if exceptionMatched:
                break

        if exceptionMatched:
            if key not in self.exceptionsMatched.keys():
                self.exceptionsMatched[key] = {
                    "exceptionCount": 1,
                    "exceptionValues": [str(actualData)],
                    "fix": fix
                }
            else:
                self.exceptionsMatched[key]["exceptionCount"] += 1
                if str(actualData) not in self.exceptionsMatched[key]["exceptionValues"]:
                    self.exceptionsMatched[key]["exceptionValues"].append(str(actualData))
        return exceptionMatched

    def __fixException(self, fix):
        self.fixedData = True
        return eval(fix)

    def __checkExact(self, key, expectedData, actualData):
        self.assertEqual(actualData, expectedData)

    def __checkEnum(self, key, enumeratedData, actualData):
        self.assertIn(actualData, enumeratedData, " from : " + str(self.parentKey))

    def __checkType(self, key, expectedType, actualData):
        expectedType = expectedType.split("|")
        actualType = type(actualData).__name__
        self.assertIn(actualType, expectedType, str(key) + " from : " + str(self.parentKey))

    def __checkPattern(self, key, pattern, actualData):
        self.assertRegex(actualData, pattern, "key: " + str(key) + " from : " + str(self.parentKey))

    def __checkMinLength(self, key, minLength, actualData):
        self.assertTrue(hasattr(actualData, '__len__'), str(key) + " does not have a length field. Cannot check minLength")
        self.assertLessEqual(minLength, len(actualData), "Minimum Length requirement not met for: " + str(key))

    def __checkMaxLength(self, key, maxLength, actualData):
        self.assertTrue(hasattr(actualData, '__len__'), str(key) + " does not have a length field. Cannot check maxLength")
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
            self.runStructureTest(expectedChildren, actualData, key, self.allowedExceptions)

    def __matchParameters(self, key, expectedParams, actualData):
        # If the exception case matches, then ignore checking any other parameters
        # This check is done first so that "exception" can be included in any order
        if "exception" in expectedParams:
            fix = expectedParams["fix"] if "fix" in expectedParams else ""
            if self.__matchException(key, expectedParams["exception"], actualData, fix):
                return
        for expectedParam in expectedParams:
            # This case is handled above, so should be skipped
            if expectedParam == "exception":
                continue
            elif expectedParam == "fix":
                actualData = self.__fixException(expectedParams["fix"]);
                continue
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
            elif expectedParam == 'enum':
                self.__checkEnum(key, expectedParams[expectedParam], actualData)
            elif expectedParam == 'children':
                self.__testChildren(key, expectedParams[expectedParam], actualData)
            else:
                self.assertTrue(False, "No expected parameters for " + key + " were tested. Malformed testing JSON.")

        return actualData

    def __addInAllowedExceptions(self, key, expectedParams):
        if self.allowedExceptions:
            for exceptionMatch, allowedException in self.allowedExceptions.copy().items():
                if allowedException["chain"] and key == allowedException["chain"][0]:
                    self.allowedExceptions[exceptionMatch]["chain"] = allowedException["chain"][1:]
                    if not self.allowedExceptions[exceptionMatch]["chain"]:
                        expectedParams["exception"] = allowedException["type"]
                        if "fix" in allowedException:
                            expectedParams["fix"] = allowedException["fix"]
                        del self.allowedExceptions[exceptionMatch]
        return expectedParams

    # start with constants.CNS2_MOP and self.cns2_data, recurse
    def runStructureTest(self, expectedData, actualData, parentKey="", allowedExceptions=[]):
        """Iterates through every key in outputted JSON and compares it to parameters set in a testing JSON"""
        self.parentKey = parentKey
        self.allowedExceptions = allowedExceptions
        # Base case - if the structure is empty or not the right type, return
        if not isinstance(expectedData, dict) or not hasattr(actualData, '__iter__') or not expectedData or not actualData:
            return actualData
        for key, value in expectedData.items():
            self.assertTrue(key in actualData, "Key not found in JSON: " + key + " (parentKey: " + str(self.parentKey) + ")")
            if isinstance(value, dict) and 'match' in value.keys():
                expectedParams = self.__addInAllowedExceptions(key, value["match"])

                actualData[key] = self.__matchParameters(key, expectedParams, actualData[key])
            else:
                actualData[key] = self.runStructureTest(value, actualData[key], "Last Key: " + key, self.allowedExceptions)

        return actualData
