"""Provides tests for cns1.py values."""
import json
import sys
import os

testing_directory = os.path.abspath(os.path.join(os.path.join(__file__, os.path.pardir), os.path.pardir))
sys.path.append(testing_directory)

from StructureTestController import StructureTestController

# Include local testing constants, adds tcl3parsers to path
import constants

ACTUAL_DATA_FILE = {}
SPECIFICATION_DATA = {}

class StructureTests(StructureTestController.StructureTestController):
    """Adds test cases to examine entire structure of JSON"""
    @classmethod
    def setUpClass(cls):
        """Opens generated output file for parser testing"""
        generatedFile = open(ACTUAL_DATA_FILE, "r")
        cls.data = json.load(generatedFile)
        cls.specData = SPECIFICATION_DATA

    def test_structure(self):
        """Run all test cases comparing the outputted JSON file against the expected structure found in constants.py"""
        self.runStructureTest(self.specData, self.data)
        print(self.data)
