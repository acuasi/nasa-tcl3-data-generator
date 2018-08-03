"""Provides tests for cns1.py values."""
import json
import sys
import os

testing_directory = os.path.abspath(os.path.join(os.path.join(__file__, os.path.pardir), os.path.pardir))
sys.path.append(testing_directory)

from StructureTestController import StructureTestController

# Include local testing constants, adds tcl3parsers to path
import constants

class TestValueTypes(StructureTestController.StructureTestController):
    """Adds test cases for value type"""

    @classmethod
    def setUpClass(cls):
        generatedFile = open(constants.OUTFILE_NAME, "r")
        cls.cns2_data = json.load(generatedFile)

    def test_structure(self):
        """Run all test cases comparing the outputted JSON file against the expected structure found in constants.py"""
        self.runStructureTest(constants.CNS2_MOP, self.cns2_data)
