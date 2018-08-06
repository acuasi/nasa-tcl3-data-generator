"""Generic testing suite runner file"""
import unittest
import os
import sys
import re
import yaml
import importlib

import constants

testing_directory = os.path.abspath(os.path.join(os.path.join(__file__, os.path.pardir), os.path.pardir))
sys.path.append(testing_directory)

parser_directory = os.path.abspath(os.path.join(os.path.join(os.path.join(__file__, os.path.pardir), os.path.pardir), os.path.pardir))
sys.path.append(parser_directory)

# import cns1

# Test Modules
import structure_tests

class Runner():
    """Executes parser and runs the testing suite"""
    def __init__(self, dataDirectory, parserName):
        """Loads all tests"""
        tests = unittest.TestSuite()
        loader = unittest.TestLoader()
        tests.addTests(loader.loadTestsFromModule(structure_tests))
        self.suite = tests
        self.dataDirectory = dataDirectory
        self.parserName = parserName
        self.flightName = ""
        # self.MI_FILE_NAME = ""
        # self.DF_FILE_NAME = ""
        # self.FIELD_VARS_NAME = ""
        # self.RADAR_FILE_NAME = ""
        # self.OUTFILE_NAME = ""
        self.parserParameters = []

    def getRequiredFlightFile(self, flightFiles, requiredFile, requirements):
        flightPath = self.dataDirectory +  "/" + self.flightName
        for fileName in flightFiles:
            for requirement in requirements:
                if requirement in fileName or re.match(requirement, fileName):
                    return flightPath + "/" + fileName
        print("Data malformed, " + requiredFile + " not found for " + self.flightName + " in " + flightPath)
        exit()

    def setFlightInfo(self, flightName, requiredFiles):
        """Adds all information and checks files for the specified flight"""
        self.flightName = flightName
        flightPath = self.dataDirectory +  "/" + self.flightName
        flightFiles = [name for name in os.listdir(flightPath)]

        for requiredFileName, requiredFileRequirements in requiredFiles.items():
            self.parserParameters.append(self.getRequiredFlightFile(flightFiles, requiredFileName, requiredFileRequirements))

        outfile = "{0}/{1}/{2}_data_{3}.json".format(self.dataDirectory, self.flightName, self.parserName, flightName.lower().replace(" ", "_"))
        self.parserParameters.append(outfile)
        constants.OUTFILE_NAME = outfile

    def __runParser(self):
        """Imports the parser module and executes it dynamically using the parameters specified in the config.yaml file"""
        params = ", ".join("'{0}'".format(param) for param in self.parserParameters)
        parser_mod = importlib.import_module(self.parserName)

        # WARNING: exec is inherently dangerous, so double check config.yaml before executing
        exec("parser_mod.generate({0})".format(params))

    def run(self):
        """Runs testing suite"""
        self.__runParser()
        runner = unittest.TextTestRunner(verbosity=3)
        return runner.run(self.suite)

def runAgainstAllSampleData(dataDirectory, parserName, parserParameters):
    """Runs test against every flight in the specified dataDirectory folder"""
    flightData = [name for name in os.listdir(dataDirectory) if os.path.isdir(dataDirectory + "/" + name)]
    flightData.sort()
    for flightName in flightData:
        testRunner = Runner(dataDirectory, parserName)
        testSet = testRunner.setFlightInfo(flightName, parserParameters)
        print("Testing against: " + flightName)
        testSet = testRunner.run()
        print("Tested against: " + flightName + "\n\n")
        failure = len(testSet.failures)
        if failure:
            break

if __name__ == '__main__':
    # flightDataDirectory = testing_directory + "/tests/example_files/cns1/SampleData"
    # outFile = "cns1_data.json"
    with open("config.yaml", "r") as config:
        options = yaml.load(config)

    if not options['run']:
        options['run'] = options['parsers'].keys()

    for parser_name in options['run']:
        flightDataDirectory = testing_directory + "/example_files/" + parser_name + "/SampleData"
        parser_config = options['parsers'][parser_name]
        runAgainstAllSampleData(flightDataDirectory, parser_name, parser_config)
