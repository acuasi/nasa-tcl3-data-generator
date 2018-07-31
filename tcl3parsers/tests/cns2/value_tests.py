"""Provides tests for cns1.py values."""
import json
import unittest

# Include local testing constants, adds tcl3parsers to path
import constants as CNS2Constant
import cns2

class TestValueTypes(unittest.TestCase):
    """Adds test cases for value type"""

    @classmethod
    def setUpClass(cls):
        generatedFile = open(CNS2Constant.OUTFILE_NAME, "r")
        cls.cns2_data = json.load(generatedFile)
