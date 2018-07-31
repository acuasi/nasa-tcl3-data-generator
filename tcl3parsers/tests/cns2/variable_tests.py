"""Provides tests for cns1.py variables."""
import json
import unittest

# Include local testing constants, adds tcl3parsers to path
import constants as CNS2Constant
import cns2

class TestVariableExistence(unittest.TestCase):
    """Make sure that all variables exist in the outputted file"""

    @classmethod
    def setUpClass(cls):
        generatedFile = open(CNS2Constant.OUTFILE_NAME, "r")
        cls.cns2_data = json.load(generatedFile)
