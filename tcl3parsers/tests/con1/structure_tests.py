"""Provides tests for con1.py values."""
import json
import sys
import os

testing_directory = os.path.abspath(os.path.join(os.path.join(__file__, os.path.pardir), os.path.pardir))
sys.path.append(testing_directory)

from StructureTestController import StructureTestController

# Include local testing constants, adds tcl3parsers to path
import constants

class StructureTests(StructureTestController.StructureTestController):
    """Adds test cases to examine entire structure of JSON"""
    @classmethod
    def setUpClass(cls):
        """Opens generated output file for parser testing"""
        generatedFile = open(constants.OUTFILE_NAME, "r")
        cls.con1_data = json.load(generatedFile)

    def test_structure(self):
        """Run all test cases comparing the outputted JSON file against the expected structure found in constants.py"""
        self.runStructureTest(constants.CON1_MOP, self.con1_data)
