import json
import sys
import os
import yaml
import importlib
from pathlib import Path

file_parsers = os.path.abspath(os.path.join(os.path.dirname(__file__), "parser_pieces/file_parsers"))
variable_parsers = os.path.abspath(os.path.join(os.path.dirname(__file__), "parser_pieces/variable_parsers"))
global_parsers = os.path.abspath(os.path.join(os.path.dirname(__file__), "parser_pieces/global_parsers"))
sys.path.append(file_parsers)
sys.path.append(variable_parsers)
sys.path.append(global_parsers)

class GenericParser():
    def __init__(self, specification, options, parserName, files):
        self.specification = specification
        self.jsonModel = self.generateDefaultModel(specification)
        self.parserName = parserName
        if self.parserName in options["parsers"]:
            self.globalParserList = options["parsers"][self.parserName]["global_parsers"] if "global_parsers" in options["parsers"][self.parserName] else []
            self.fileParserList = options["parsers"][self.parserName]["file_parsers"] if "file_parsers" in options["parsers"][self.parserName] else []
            self.variableParserList = options["parsers"][self.parserName]["variable_parsers"] if "variable_parsers" in options["parsers"][self.parserName] else []
        elif self.parserName in options["sub_parsers"]:
            self.globalParserList = options["sub_parsers"][self.parserName]["global_parsers"] if "global_parsers" in options["sub_parsers"][self.parserName] else []
            self.fileParserList = options["sub_parsers"][self.parserName]["file_parsers"] if "file_parsers" in options["sub_parsers"][self.parserName] else []
            self.variableParserList = options["sub_parsers"][self.parserName]["variable_parsers"] if "variable_parsers" in options["sub_parsers"][self.parserName] else []
        else:
            raise Exception("Could not find parser: " + self.parserName + "!")
        self.files = files
        self.exceptionList = {}

    def generateDefaultModel(self, specModel=None):
        """Uses the specification to generate a JSON model with default type values filled in"""
        if specModel is None:
            specModel = self.specification

        tempJSON = {}
        for key, value in specModel.items():
            if isinstance(value, dict):
                if "match" in value:
                    if "type" in value["match"]:
                        variableType = value['match']['type'].split("|")[0]
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
        if not isinstance(self.fileParserList, dict):
            return
        # Since Python is lazily evaluated, this is actually just a reference to the model,
        # which makes file parsers much more efficient than if they had to copy a potentially
        # massive model every time they were executed.
        jsonModel = self.jsonModel
        for shortname, source in self.fileParserList.items():
            file_parser_module = importlib.import_module(source['parser'])
            file_path = source['path']
            jsonModel = eval("file_parser_module.{0}(jsonModel, file_path)".format(source['parser']))
            if not jsonModel:
                raise Exception("Error executing: " + source['parser'] + ", parser did not return the model.")

        self.jsonModel = jsonModel

    def executeGlobalParsers(self):
        if not isinstance(self.globalParserList, list):
            return
        jsonModel = self.jsonModel
        for parser_name in self.globalParserList:
            file_parser_module = importlib.import_module(parser_name)
            files = self.files
            jsonModel = eval("file_parser_module.{0}(jsonModel, files)".format(parser_name))
            if not jsonModel:
                raise Exception("Error executing: " + parser_name + ", parser did not return the model.")
        self.jsonModel = jsonModel

    def executeVariableParsers(self):
        if not isinstance(self.variableParserList, dict):
            return
        for masterVariable, source in self.variableParserList.items():
            if "exact" in source and source["exact"]:
                if "[" in masterVariable and "]" in masterVariable:
                    masterVariable = masterVariable.replace("[", "['").replace("]", "']")
                    topLevelMasterVariable = masterVariable[:masterVariable.find("[")]
                    masterVariable = "['" + topLevelMasterVariable + "']" + masterVariable[masterVariable.find("["):]
                    if isinstance(source["exact"], str) and source["exact"][0] != '"' and source["exact"][-1] != '"':
                        source["exact"] = '"{0}"'.format(source["exact"])
                    exec("self.jsonModel{0} = {1}".format(masterVariable, source["exact"]))
                else:
                    self.jsonModel[masterVariable] = source["exact"]
            if "exception" in source:
                if "[" in masterVariable and "]" in masterVariable:
                    masterVariable = masterVariable.replace("[", "['").replace("]", "']")
                    topLevelMasterVariable = masterVariable[:masterVariable.find("[")]
                    masterVariable = "['" + topLevelMasterVariable + "']" + masterVariable[masterVariable.find("["):]
                else:
                    masterVariable = "['" + masterVariable + "']"

                exceptionKeyMatchChain = [exceptionMatch for exceptionMatch in masterVariable.replace("['", "").split("']") if exceptionMatch]
                self.exceptionList[masterVariable] = {
                    "type": source["exception"],
                    "chain": exceptionKeyMatchChain
                }
                if "fix" in source:
                    self.exceptionList[masterVariable]["fix"] = source["fix"]
                    continue

            if "parser" in source:
                variable_parser_module = importlib.import_module(source['parser'])
                self.jsonModel[masterVariable] = eval("variable_parser_module.{0}(self.files)".format(source['parser']))

    def generate(self):
        """ Iterate through global and file parsers and execute them by passing them the jsonModel and setting it equal to whatever they return.
        Then iterate through variable parsers and set the specified variable equal to what they return. """
        self.executeVariableParsers()
        self.executeFileParsers()
        self.executeGlobalParsers()

        if "flight_data" in self.parserName.lower():
            if "auxiliaryUASOperation" in self.jsonModel.keys() and "takeOffTime" in self.jsonModel["auxiliaryUASOperation"]:
                takeOffTime = self.jsonModel["auxiliaryUASOperation"]["takeOffTime"]
                # print(takeOffTime)
                # exit()

        return self.jsonModel

    def getAllowedExceptions(self):
        return self.exceptionList

def generate(specJSON, options, parserName, files):
    parser = GenericParser(specJSON, options, parserName, files)
    return parser.generate()
