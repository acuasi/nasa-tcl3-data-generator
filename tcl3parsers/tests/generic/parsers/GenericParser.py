import json
import sys
import os
import yaml
import importlib

parser_file_pieces = "parser_pieces/file_parsers"
parser_variable_pieces = "parser_pieces/variable_parsers"
sys.path.append(parser_file_pieces)
sys.path.append(parser_variable_pieces)

class GenericParser():
    def __init__(self, specification, options, parserName):
        self.specification = specification
        self.jsonModel = self.generateDefaultModel(specification)
        self.parserName = parserName
        self.fileParserList = options["parsers"][self.parserName]["file_parsers"]
        self.variableParserList = options["parsers"][self.parserName]["variable_parsers"]

    def generateDefaultModel(self, specModel=None):
        """Uses the specification to generate a JSON model with default type values filled in"""
        if specModel is None:
            specModel = self.specification

        tempJSON = {}
        for key, value in specModel.items():
            if isinstance(value, dict):
                if "match" in value:
                    if "type" in value["match"]:
                        variableType = value['match']['type']
                        tempJSON[key] = eval("{0}()".format(variableType))
                    else:
                        tempJSON[key] = None
                else:
                    tempJSON[key] = self.generateDefaultModel(value)
                    continue
            else:
                tempJSON[key] = value
        return tempJSON

    def executeFileParsers(self):
        jsonModel = self.jsonModel
        for shortname, source in self.fileParserList.items():
            file_parser_module = importlib.import_module(source['parser'])

            jsonModel = eval("file_parser_module.{0}(jsonModel, filePath)".format(source['parser']))

        self.jsonModel = jsonModel

    def executeVariableParsers(self):
        for masterVariable, source in self.variableParserList.items():
            if source["exact"]:
                self.jsonModel[masterVariable] = source["exact"]
            else:
                variable_parser_module = importlib.import_module(source['parser'])
                # files = {}
                # TODO: have files be an array of all of the files, identified by their shortnames
                self.jsonModel[masterVariable] = eval("variable_parser_module.{0}(files)".format(source['parser']))



    def generate(self):
        # Iterate through file parsers and execute them by passing them the jsonModel and setting it equal to whatever they return
        # Then iterate through variable parsers and set the specified variable equal to what they return
        self.executeFileParsers()
        self.executeVariableParsers()


def generate(specJSON, options, parserName):
    parser = GenericParser(specJSON, options, parserName)
    parser.generate()
    # print(json.dumps(parser., indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    # options file will be passed in
    with open("../config.yaml", "r") as configReader:
        opts = yaml.load(configReader)

    opts['parsers']['cns1']['file_parsers']['MI_FILE_NAME']['file_path'] = "../../example_files/cns1/SampleData/Flight 1/2018-04-27 11-16-16_mission_insight.csv"
    # this will be passed in
    parser_name = "cns1"

    # spec file will be passed in
    with open("../specifications/cns1_specification.json", "r") as specReader:
        spec_json = json.load(specReader)
        generate(spec_json, opts, parser_name)
