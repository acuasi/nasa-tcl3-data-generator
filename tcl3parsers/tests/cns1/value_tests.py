"""Provides tests for cns1.py values."""
import json
import unittest

# Include local testing constants
import constants as CNS1Constant

class TestValueTypes(unittest.TestCase):
    """Adds test cases for value type"""

    @classmethod
    def setUpClass(cls):
        generatedFile = open(CNS1Constant.OUTFILE_NAME, "r")
        cls.cns1_data = json.load(generatedFile)

    def test_json_objs_str(self):
        """Check json objects with values of type str."""
        for key in CNS1Constant.JSON_OBJ_STR:
            self.assertIsInstance(self.cns1_data[key], str)

    def test_json_objs_dict(self):
        """Check json objects with values of type dict."""
        for key in CNS1Constant.JSON_OBJ_DICT:
            self.assertIsInstance(self.cns1_data[key], dict)

    def test_json_obj_lists(self):
        """Check json objects with values of type list."""
        for key in CNS1Constant.JSON_OBJ_LISTS:
            self.assertIsInstance(self.cns1_data[key], list)

    def test_basic_values(self):
        """Check that 'basic' object values are of type str."""
        for _, value in self.cns1_data["basic"].items():
            self.assertIsInstance(value, str)

    def test_planned_contin_values(self):
        """Check that 'plannedContingency' object vavlues of type list."""
        for _, value in self.cns1_data["plannedContingency"].items():
            self.assertIsInstance(value, (list, type(None)))

    def test_timestamps(self):
        """Check that all timestamp values are of type str."""
        for var in CNS1Constant.JSON_OBJ_LISTS:
            for item in self.cns1_data[var]:
                # Catch 'loiter' lists that are of type None
                self.assertNotIsInstance(item, type(None))
                for key, value in item.items():
                    if key == "ts":
                        self.assertIsInstance(value, str)

    def test_nonlist_values(self):
        """Check non-list value types."""
        keys = ["cns1TestType", "contingencyResponse", "contingencyLoiterType",
                "estimatedTimeToVerifyManeuver"]
        for key in keys:
            if self.cns1_data[key]:
                for item in self.cns1_data[key]:
                    # Catch 'loiter' lists that are of type None
                    self.assertNotIsInstance(item, type(None))
                    for k, v in item.items():
                        if k != "ts":
                            self.assertIsInstance(v, (int, float, type(None)))

    def test_list_values(self):
        """Check non-list value types."""
        keys = ["contingencyCause", "contingencyLoiterAlt", "contingencyLoiterRadius"]
        for key in keys:
            if self.cns1_data[key]:
                for item in self.cns1_data[key]:
                    # Catch 'loiter' lists that are of type None
                    self.assertNotIsInstance(item, type(None))
                    for k, v in item.items():
                        if k != "ts":
                            self.assertIsInstance(v[0], (int, float))

    def test_str_values(self):
        """Check non-list value types."""
        keys = ["maneuverCommand", "primaryLinkDescription", "redundantLinkDescription"]
        for key in keys:
            for item in self.cns1_data[key]:
                # Catch 'loiter' lists that are of type None
                self.assertNotIsInstance(item, type(None))
                for k, v in item.items():
                    if k != "ts":
                        self.assertIsInstance(v[0], str)
