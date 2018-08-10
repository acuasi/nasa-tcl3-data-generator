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
    def __init__(self, dataDirectory, options, parserName, outFile="", parentParserName="", outputFolderPrepend=""):
        """Loads all tests"""
        tests = unittest.TestSuite()
        loader = unittest.TestLoader()
        tests.addTests(loader.loadTestsFromModule(structure_tests))
        self.suite = tests
        self.dataDirectory = dataDirectory
        self.parserName = parserName
        self.parentParserName = parentParserName
        self.flightName = ""
        self.parserParameters = []
        self.specification = {}
        self.options = options
        self.files = {}
        self.outFile = outFile
        self.parserFlightOutputFolder = ""
        self.outputFolderPrepend = outputFolderPrepend
        self.isSubParser = parserName not in options['parsers']

    def getRequiredFlightFile(self, flightFiles, requiredFile, requirements):
        flightPath = self.dataDirectory +  "/" + self.flightName
        for fileName in flightFiles:
            for requirement in requirements:
                if requirement in fileName or re.match(requirement, fileName):
                    return flightPath + "/" + fileName
        print("Data malformed, " + requiredFile + " not found for " + self.flightName + " in " + flightPath)
        exit()

    def setFlightInfo(self, flightName):
        """Adds all information and checks files for the specified flight"""
        cache_specs = self.options['cache_specifications']
        outputFolder = self.options['output_directory']
        specCacheDir = self.options['specification_cache_directory']
        specNameOverride = ""
        if not self.isSubParser:
            requiredFiles = self.options['parsers'][self.parserName]['required_files']
            specLink = self.options['parsers'][self.parserName]['swagger_hub_spec']
            if "name_override" in self.options['parsers'][self.parserName]:
                specNameOverride = self.options['parsers'][self.parserName]['name_override']
        else:
            requiredFiles = self.options['sub_parsers'][self.parserName]['required_files']
            specLink = self.options['sub_parsers'][self.parserName]['swagger_hub_spec']
            if "name_override" in self.options['sub_parsers'][self.parserName]:
                specNameOverride = self.options['sub_parsers'][self.parserName]['name_override']

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

        parserName = self.parserName if self.parentParserName == "" else self.parentParserName
        parserOutputFolder = "{0}/{1}".format(outputFolder, parserName)
        if not os.path.isdir(parserOutputFolder):
            os.mkdir(parserOutputFolder)

        escapedFlightName = flightName.lower().replace(" ", "_")

        # Only add separator if there is something to prepend
        if self.outputFolderPrepend:
            self.outputFolderPrepend += "_"
        parserFlightOutputFolder = "{0}/{1}".format(parserOutputFolder, self.outputFolderPrepend + escapedFlightName)

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

        specName = specNameOverride if specNameOverride else self.parserName

        spec_output_name = "{0}/{1}_specification.json".format(specCacheDir, specName)
        if cache_specs and os.path.isfile(spec_output_name):
            specification = json.load(open(spec_output_name, "r"))
        else:
            # First check if user set an override name. If so, this is the mopName. If not, then check to see if the parser name ends in a number
            # if it does (like in the case of cns1) then try using the {parserName}_MOP as the mopName. If it is still different, then just use
            # an uppercase version of the parserName (ex. FLIGHT_DATA)
            if specNameOverride:
                mopName = specName
            elif re.match(r".+[0-9]", specName):
                mopName = "{0}_MOP".format(specName.upper())
            else:
                mopName = specName.upper()
            spec_parser = SwaggerHubParser.SwaggerHubParser(mopName, link=specLink)
            specification = spec_parser.parse()
            if cache_specs:
                with open(spec_output_name, "w") as jsonWriter:
                    jsonWriter.write(json.dumps(specification, indent=4, separators=(',', ': ')))

        structure_tests.SPECIFICATION_DATA = specification
        self.specification = specification

    def __runParser(self):
        """Imports the parser module and executes it dynamically using the parameters specified in the config.yaml file"""
        genericParser = GenericParser.GenericParser(self.specification, self.options, self.parserName, self.files)
        parsedJSON = genericParser.generate()

        allowedExceptions = genericParser.getAllowedExceptions()
        structure_tests.ALLOWED_EXCEPTIONS = allowedExceptions

        with open(self.outFile, "w") as jsonWriter:
            jsonWriter.write(json.dumps(parsedJSON, indent=4, separators=(',', ': ')))


    def run(self):
        """Runs testing suite"""
        self.__runParser()
        structure_tests.OUTFILE = self.outFile
        runner = unittest.TextTestRunner(verbosity=3)
        return runner.run(self.suite)

def runAgainstSingleFlight(flightName, dataDirectory, options, parserName, outFile="", parentParserName="", outputFolderPrepend=""):
    # If there aren't any required files, then be lazy and stop immediately
    if parserName in options['parsers'] and 'required_files' not in options['parsers'][parserName]:
        return
    elif parserName in options['sub_parsers'] and 'required_files' not in options['sub_parsers'][parserName]:
        return

    testRunner = Runner(dataDirectory, options, parserName, outFile, parentParserName, outputFolderPrepend)
    testSet = testRunner.setFlightInfo(flightName)
    print("Testing against: " + flightName)
    testSet = testRunner.run()
    print("Tested against: " + flightName + "\n\n")
    return len(testSet.failures) != 0


def runSubParsers(flightName, dataDirectory, options, parserName, outputFolderPrepend):
    subParsers = options["parsers"][parserName]["sub_parsers"]
    if isinstance(subParsers, list):
        for subParser in subParsers:
            if isinstance(subParser, str):
                subParserName = subParser
            elif isinstance(subParser, dict):
                subParserName = list(subParser)[0]
                if isinstance(subParser[subParserName], dict) and "if_in" in subParser[subParserName]:
                    ifInConditions = subParser[subParserName]["if_in"]
                    matchesIfInCondition = False
                    for ifInCondition in ifInConditions:
                        fullPath = dataDirectory + "/" + flightName
                        # Only run if matches a condition
                        if ifInCondition in fullPath:
                            matchesIfInCondition = True
                            break
                    if not matchesIfInCondition:
                        continue
            else:
                print("Misconfigured sub_parsers option in parsers section, skipping...")
                return False
            subParserOutputFile = subParserName + ".json"
            print("Starting " + parserName + "'s sub-parser: " + subParserName)
            failure = runAgainstSingleFlight(flightName, dataDirectory, options, subParserName, subParserOutputFile, parserName, outputFolderPrepend)
            if failure:
                return failure
    elif isinstance(subParsers, str):
        subParserName = subParsers
        subParserOutputFile = subParserName + ".json"
        print("Starting " + parserName + "'s sub-parser: " + subParserName)
        return runAgainstSingleFlight(flightName, dataDirectory, options, subParserName, subParserOutputFile, parserName, outputFolderPrepend)

    return False


def runAgainstAllData(dataDirectory, options, parserName, outputFolderPrepend=[]):
    """Runs test against every flight in the specified dataDirectory folder"""
    flightData = [name for name in os.listdir(dataDirectory) if os.path.isdir(dataDirectory + "/" + name)]

    mainFlightDataDirectory = True
    # Find the lowest level directory that doesn't have any subdirectories in it and then run against its parent directory, ignore any directory with subdirectories
    for directoryItem in flightData:
        subDirectory = dataDirectory + "/" + directoryItem
        if os.path.isdir(subDirectory):
            # We want to find the directory that contains directories that DONT contain directories, so we need to perform a look ahead.
            # When it finally reaches the data directory containing said folders, then this should only check the first folder and break once.
            # This means that the bottom level flight directories (technically only the first one) cannot have folders within them.
            for subDirectoryItem in os.listdir(subDirectory):
                if os.path.isdir(subDirectory + "/" + subDirectoryItem):
                    tempOutputFolderPrepend = outputFolderPrepend[:]
                    tempOutputFolderPrepend.append(directoryItem.lower().replace(" ", "_"))
                    runAgainstAllData(subDirectory, options, parserName, tempOutputFolderPrepend)
                    mainFlightDataDirectory = False
                    break
            if mainFlightDataDirectory:
                break

    if not mainFlightDataDirectory:
        return

    outputFolderPrepend = "_".join(outputFolderPrepend)

    flightData.sort()
    for flightName in flightData:
        failure = runAgainstSingleFlight(flightName, dataDirectory, options, parserName, outputFolderPrepend=outputFolderPrepend)
        if failure:
            break

        if "sub_parsers" in options["parsers"][parserName].keys():
            failure = runSubParsers(flightName, dataDirectory, options, parserName, outputFolderPrepend)
            # print(options["parsers"][parserName]["sub_parser"])
            #
            # return
            # subParserName = options["parsers"][parserName]["sub_parser"]
            # subParserOutputFile = subParserName + ".json"
            #
            # print("Starting " + parserName + "'s sub-parser: " + subParserName)
            #
            # failure = runAgainstSingleFlight(flightName, dataDirectory, options, subParserName, subParserOutputFile, parserName, outputFolderPrepend)
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
        runAgainstAllData(flightDataDirectory, options, parser_name)

if __name__ == '__main__':
    loadConfigAndRun()
