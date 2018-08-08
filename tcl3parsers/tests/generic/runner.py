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

generic_parser_directory = os.path.abspath(os.path.join(os.path.join(__file__, os.path.pardir), "parsers"))
sys.path.append(generic_parser_directory)

import GenericParser

# Test Modules
import structure_tests

class Runner():
    """Executes parser and runs the testing suite"""
    def __init__(self, dataDirectory, options, parserName, outFile=""):
        """Loads all tests"""
        tests = unittest.TestSuite()
        loader = unittest.TestLoader()
        tests.addTests(loader.loadTestsFromModule(structure_tests))
        self.suite = tests
        self.dataDirectory = dataDirectory
        self.parserName = parserName
        self.flightName = ""
        self.parserParameters = []
        self.specification = {}
        self.options = options
        self.files = {}
        self.outFile = outFile
        self.parserFlightOutputFolder = ""

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
            file_path = self.getRequiredFlightFile(flightFiles, requiredFileName, requiredFileRequirements)
            self.parserParameters.append(file_path)

            if self.parserName in self.options['parsers']:
                file_parsers = self.options['parsers'][self.parserName]['file_parsers']
                if requiredFileName in file_parsers.keys():
                    self.options['parsers'][self.parserName]['file_parsers'][requiredFileName]['path'] = file_path
            else:
                file_parsers = self.options['sub_parsers'][self.parserName]['file_parsers']
                if requiredFileName in file_parsers.keys():
                    self.options['sub_parsers'][self.parserName]['file_parsers'][requiredFileName]['path'] = file_path

            self.files[requiredFileName] = file_path

        if not os.path.isdir(outputFolder):
            os.mkdir(outputFolder)

        parserOutputFolder = "{0}/{1}".format(outputFolder, self.parserName)
        if not os.path.isdir(parserOutputFolder):
            os.mkdir(parserOutputFolder)

        escapedFlightName = flightName.lower().replace(" ", "_")

        parserFlightOutputFolder = "{0}/{1}".format(parserOutputFolder, escapedFlightName)
        if not os.path.isdir(parserFlightOutputFolder):
            os.mkdir(parserFlightOutputFolder)

        self.parserFlightOutputFolder = parserFlightOutputFolder

        if self.outFile == "":
            outfile = "{0}/{1}_data_{2}.json".format(parserFlightOutputFolder, self.parserName, escapedFlightName)
        else:
            outfile = "{0}/{1}".format(parserFlightOutputFolder, self.outFile)
        self.outFile = outfile
        self.parserParameters.append(outfile)
        structure_tests.ACTUAL_DATA_FILE = outfile

        if not os.path.isdir(specCacheDir):
            os.mkdir(specCacheDir)

        spec_output_name = "{0}/{1}_specification.json".format(specCacheDir, self.parserName)
        if cache_specs and os.path.isfile(spec_output_name):
            specification = json.load(open(spec_output_name, "r"))
        else:
            if re.match(r".+[0-9]", self.parserName):
                mopName = "{0}_MOP".format(self.parserName.upper())
            else:
                mopName = self.parserName.upper()
            spec_parser = SwaggerHubParser.SwaggerHubParser(mopName, link=specLink)
            specification = spec_parser.parse()
            if cache_specs:
                with open(spec_output_name, "w") as jsonWriter:
                    jsonWriter.write(json.dumps(specification, indent=4, separators=(',', ': ')))

        structure_tests.SPECIFICATION_DATA = specification
        self.specification = specification

    def __runParser(self):
        """Imports the parser module and executes it dynamically using the parameters specified in the config.yaml file"""
        # params = ", ".join("'{0}'".format(param) for param in self.parserParameters)
        # parser_module = importlib.import_module(self.parserName)

        # parsedJSON = GenericParser.generate(self.specification, self.options, self.parserName, self.files)

        genericParser = GenericParser.GenericParser(self.specification, self.options, self.parserName, self.files)
        parsedJSON = genericParser.generate()

        allowedExceptions = genericParser.getAllowedExceptions()
        structure_tests.ALLOWED_EXCEPTIONS = allowedExceptions

        with open(self.outFile, "w") as jsonWriter:
            jsonWriter.write(json.dumps(parsedJSON, indent=4, separators=(',', ': ')))


    def run(self):
        """Runs testing suite"""
        self.__runParser()
        runner = unittest.TextTestRunner(verbosity=3)
        return runner.run(self.suite)

def runAgainstSingleFlight(flightName, dataDirectory, options, parserName, parserRequiredFiles, specLink, cache_specs, outputFolder, specCacheDir, outFile=""):
    testRunner = Runner(dataDirectory, options, parserName, outFile)
    testSet = testRunner.setFlightInfo(flightName, parserRequiredFiles, specLink, cache_specs, outputFolder, specCacheDir)
    print("Testing against: " + flightName)
    testSet = testRunner.run()
    print("Tested against: " + flightName + "\n\n")
    return len(testSet.failures) != 0

def runAgainstAllData(dataDirectory, options, parserName, parserRequiredFiles, specLink, cache_specs, outputFolder, specCacheDir):
    """Runs test against every flight in the specified dataDirectory folder"""
    flightData = [name for name in os.listdir(dataDirectory) if os.path.isdir(dataDirectory + "/" + name)]
    flightData.sort()
    for flightName in flightData:
        failure = runAgainstSingleFlight(flightName, dataDirectory, options, parserName, parserRequiredFiles, specLink, cache_specs, outputFolder, specCacheDir)
        if failure:
            break

        if "sub_parser" in options["parsers"][parserName].keys():
            subParserName = options["parsers"][parserName]["sub_parser"]
            subParserRequiredFiles = options['sub_parsers'][subParserName]['required_files']
            subParserSpecLink = options['sub_parsers'][subParserName]['swagger_hub_spec']
            subParserOutputFile = subParserName + ".json"

            print("Starting Sub-parser: " + subParserName)

            failure = runAgainstSingleFlight(flightName, dataDirectory, options, subParserName,
                                             subParserRequiredFiles, subParserSpecLink, cache_specs, outputFolder, specCacheDir, subParserOutputFile)
            if failure:
                break


def loadConfigAndRun():
    """Loads the config file and runs testing/generation for all parsers specified in the config"""
    with open("config.yaml", "r") as config:
        options = yaml.load(config)

    if not options['run']:
        options['run'] = options['parsers'].keys()

    for parser_name in options['run']:
        flightDataDirectory = testing_directory + "/" + options["parent_data_directory"] + "/" + parser_name + "/" + options['flight_data_directory']
        parser_required_files = options['parsers'][parser_name]['required_files']
        specification_link = options['parsers'][parser_name]['swagger_hub_spec']
        runAgainstAllData(flightDataDirectory, options, parser_name, parser_required_files,
                          specification_link, options['cache_specifications'], options['output_directory'], options['specification_cache_directory'])

if __name__ == '__main__':
    loadConfigAndRun()
