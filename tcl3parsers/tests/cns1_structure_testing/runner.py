"""Testing suite runner file for cns1"""
import unittest
import os
import sys
import re

import constants

# TCL3PARSERS_PATH = os.path.dirname(os.path.realpath("../"))
# sys.path.append(TCL3PARSERS_PATH)

testing_directory = os.path.abspath(os.path.join(os.path.join(__file__, os.path.pardir), os.path.pardir))
sys.path.append(testing_directory)

SAMPLEDATAPATH = testing_directory + "/tests/example_files/cns1/SampleData"
OUTFILENAME = "cns1_data.json"

import cns1

# Test Modules
import structure_tests

class Runner():
    """Executes parser and runs the testing suite"""
    def __init__(self):
        """Loads all tests"""
        tests = unittest.TestSuite()
        loader = unittest.TestLoader()
        tests.addTests(loader.loadTestsFromModule(structure_tests))
        self.suite = tests
        self.sampleDataPath = SAMPLEDATAPATH
        self.sampleFlightName = ""
        self.MI_FILE_NAME = ""
        self.DF_FILE_NAME = ""
        self.FIELD_VARS_NAME = ""
        self.RADAR_FILE_NAME = ""
        self.OUTFILE_NAME = ""

    def setFlightInfo(self, flightName):
        """Sets the name of the flight folder to use under Sample Data"""
        self.sampleFlightName = flightName
        sampleFlightPath = self.sampleDataPath +  "/" + self.sampleFlightName
        sampleFlightFiles = [name for name in os.listdir(sampleFlightPath)]
        for fileName in sampleFlightFiles:
            if "mission_insight.csv" in fileName or re.match(r'^CNS1_.+Flight.+\.csv', fileName):
                self.MI_FILE_NAME = sampleFlightPath + "/" + fileName

            elif ".log" in fileName:
                self.DF_FILE_NAME = sampleFlightPath + "/" + fileName

            elif "field_vars.csv" in fileName:
                self.FIELD_VARS_NAME = sampleFlightPath + "/" + fileName
        if not self.MI_FILE_NAME:
            print("Sample data malformed, Mission File not found for " + self.sampleFlightName)
            exit()
        elif not self.DF_FILE_NAME:
            print("Sample data malformed, Data File not found for " + self.sampleFlightName)
            exit()
        self.OUTFILE_NAME = self.sampleDataPath + "/" + self.sampleFlightName + "/" + OUTFILENAME
        constants.OUTFILE_NAME = self.OUTFILE_NAME

    def __runParser(self):
        """Runs parser"""
        cns1.generate(self.MI_FILE_NAME,
                      self.DF_FILE_NAME,
                      self.FIELD_VARS_NAME,
                      self.OUTFILE_NAME)

    def run(self):
        """Runs testing suite"""
        self.__runParser()
        runner = unittest.TextTestRunner(verbosity=3)
        return runner.run(self.suite)

def runAgainstAllSampleData():
    """Run tests against all data in the example_files/cns1/SampleData folder"""
    sampleFlightData = [name for name in os.listdir(SAMPLEDATAPATH) if os.path.isdir(SAMPLEDATAPATH + "/" + name)]
    sampleFlightData.sort()
    for sampleFlightName in sampleFlightData:
        testRunner = Runner()
        testSet = testRunner.setFlightInfo(sampleFlightName)
        print("Testing against: " + sampleFlightName)
        testSet = testRunner.run()
        print("Tested against: " + sampleFlightName + "\n\n")
        failure = len(testSet.failures)
        if failure:
            break

if __name__ == '__main__':
    runAgainstAllSampleData()
