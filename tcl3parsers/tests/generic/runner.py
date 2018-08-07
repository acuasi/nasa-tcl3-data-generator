"""Generic testing suite runner file"""
import unittest
import os
import sys
import re
import yaml
import importlib
import json

testing_directory = os.path.abspath(os.path.join(os.path.join(__file__, os.path.pardir), os.path.pardir))
sys.path.append(testing_directory)

from SwaggerHubParser import parser as SwaggerHubParser

parser_directory = os.path.abspath(os.path.join(os.path.join(os.path.join(__file__, os.path.pardir), os.path.pardir), os.path.pardir))
sys.path.append(parser_directory)

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
        self.parserParameters = []

    def getRequiredFlightFile(self, flightFiles, requiredFile, requirements):
        flightPath = self.dataDirectory +  "/" + self.flightName
        for fileName in flightFiles:
            for requirement in requirements:
                if requirement in fileName or re.match(requirement, fileName):
                    return flightPath + "/" + fileName
        print("Data malformed, " + requiredFile + " not found for " + self.flightName + " in " + flightPath)
        exit()

    def setFlightInfo(self, flightName, requiredFiles, specLink, cache_specs, outputFolder, specCacheDir):
        """Adds all information and checks files for the specified flight"""
        self.flightName = flightName
        flightPath = self.dataDirectory +  "/" + self.flightName
        flightFiles = [name for name in os.listdir(flightPath)]

        for requiredFileName, requiredFileRequirements in requiredFiles.items():
            self.parserParameters.append(self.getRequiredFlightFile(flightFiles, requiredFileName, requiredFileRequirements))

        if not os.path.isdir(outputFolder):
            os.mkdir(outputFolder)

        parserOutputFolder = "{0}/{1}".format(outputFolder, self.parserName)
        if not os.path.isdir(parserOutputFolder):
            os.mkdir(parserOutputFolder)

        outfile = "{0}/{1}/{1}_data_{2}.json".format(outputFolder, self.parserName, flightName.lower().replace(" ", "_"))
        self.parserParameters.append(outfile)
        structure_tests.ACTUAL_DATA_FILE = outfile

        if not os.path.isdir(specCacheDir):
            os.mkdir(specCacheDir)

        spec_output_name = "{0}/{1}_specification.json".format(specCacheDir, self.parserName)
        if cache_specs and os.path.isfile(spec_output_name):
            specification = json.load(open(spec_output_name, "r"))
        else:
            mopName = "{0}_MOP".format(self.parserName.upper())
            spec_parser = SwaggerHubParser.SwaggerHubParser(mopName, link=specLink)
            specification = spec_parser.parse()
            if cache_specs:
                with open(spec_output_name, "w") as jsonWriter:
                    jsonWriter.write(json.dumps(specification, indent=4, separators=(',', ': ')))

        structure_tests.SPECIFICATION_DATA = specification

    def __runParser(self):
        """Imports the parser module and executes it dynamically using the parameters specified in the config.yaml file"""
        params = ", ".join("'{0}'".format(param) for param in self.parserParameters)
        parser_module = importlib.import_module(self.parserName)

        # TODO: Call the generic parser, passing in the necessary params
        # iterate through the file_parsers options and replace the shortname with the actual filename before calling parser

        # WARNING: exec is inherently dangerous, so double check config.yaml before executing
        exec("parser_module.generate({0})".format(params))

    def run(self):
        """Runs testing suite"""
        self.__runParser()
        runner = unittest.TextTestRunner(verbosity=3)
        return runner.run(self.suite)

def runAgainstAllSampleData(dataDirectory, parserName, parserParameters, specLink, cache_specs, outputFolder, specCacheDir):
    """Runs test against every flight in the specified dataDirectory folder"""
    flightData = [name for name in os.listdir(dataDirectory) if os.path.isdir(dataDirectory + "/" + name)]
    flightData.sort()
    for flightName in flightData:
        testRunner = Runner(dataDirectory, parserName)
        testSet = testRunner.setFlightInfo(flightName, parserParameters, specLink, cache_specs, outputFolder, specCacheDir)
        print("Testing against: " + flightName)
        testSet = testRunner.run()
        print("Tested against: " + flightName + "\n\n")
        failure = len(testSet.failures)
        if failure:
            break

def loadConfigAndRun():
    """Loads the config file and runs testing/generation for all parsers specified in the config"""
    with open("config.yaml", "r") as config:
        options = yaml.load(config)

    if not options['run']:
        options['run'] = options['parsers'].keys()

    for parser_name in options['run']:
        flightDataDirectory = testing_directory + "/example_files/" + parser_name + "/SampleData"
        parser_required_files = options['parsers'][parser_name]['required_files']
        specification_link = options['parsers'][parser_name]['swagger_hub_spec']
        runAgainstAllSampleData(flightDataDirectory, parser_name, parser_required_files,
                                specification_link, options['cache_specifications'], options['output_directory'], options['specification_cache_directory'])

if __name__ == '__main__':
    loadConfigAndRun()
