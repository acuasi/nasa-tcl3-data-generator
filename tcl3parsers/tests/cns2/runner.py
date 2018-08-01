"""Testing suite runner file for cns2"""
import unittest
import os
import sys

import constants

TCL3PARSERS_PATH = os.path.dirname(os.path.realpath("../"))
sys.path.append(TCL3PARSERS_PATH)

SAMPLEDATAPATH = TCL3PARSERS_PATH + "/tests/example_files/cns2/SampleData"
OUTFILENAME = "cns2_data.json"

import cns2

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

    def setFlightName(self, flightName):
        """Sets the name of the flight folder to use under Sample Data"""
        self.sampleFlightName = flightName
        sampleFlightPath = self.sampleDataPath +  "/" + self.sampleFlightName
        sampleFlightFiles = [name for name in os.listdir(sampleFlightPath)]
        for fileName in sampleFlightFiles:
            if "mission_insight.csv" in fileName:
                self.MI_FILE_NAME = sampleFlightPath + "/" + fileName

            elif ".log" in fileName:
                self.DF_FILE_NAME = sampleFlightPath + "/" + fileName

            elif "field_vars.csv" in fileName:
                self.FIELD_VARS_NAME = sampleFlightPath + "/" + fileName

            elif "Radar Flight" in fileName:
                self.RADAR_FILE_NAME = sampleFlightPath + "/" + fileName

        self.OUTFILE_NAME = self.sampleDataPath + "/" + self.sampleFlightName + "/" + OUTFILENAME
        constants.OUTFILE_NAME = self.OUTFILE_NAME

    def __runParser(self):
        """Runs parser"""
        cns2.generate(self.MI_FILE_NAME,
                      self.DF_FILE_NAME,
                      self.FIELD_VARS_NAME,
                      self.RADAR_FILE_NAME,
                      self.OUTFILE_NAME)

    def run(self):
        """Runs testing suite"""
        self.__runParser()
        runner = unittest.TextTestRunner(verbosity=3)
        return runner.run(self.suite)

def runAgainstAllSampleData():
    """Run tests against all data in the example_files/cns2/SampleData folder"""
    sampleFlightData = [name for name in os.listdir(SAMPLEDATAPATH) if os.path.isdir(SAMPLEDATAPATH + "/" + name)]
    for sampleFlightName in sampleFlightData:
        testRunner = Runner()
        testset = testRunner.setFlightName(sampleFlightName)
        print("Testing against: " + sampleFlightName)
        testset = testRunner.run()
        print("Tested against: " + sampleFlightName + "\n\n")
        failure = len(testset.failures)
        if failure:
            break

if __name__ == '__main__':
    runAgainstAllSampleData()
