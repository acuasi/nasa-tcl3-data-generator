"""Provides tests for cns1.py variables."""
import json
import unittest

# Include local testing constants
import constants as CNS1Constant

class TestVariableExistence(unittest.TestCase):
    """Make sure that all variables exist in the outputted file"""

    @classmethod
    def setUpClass(cls):
        generatedFile = open(CNS1Constant.OUTFILE_NAME, "r")
        cls.cns1_data = json.load(generatedFile)

    def test_json_objs(self):
        """Verify all high-level JSON objects exist in output file."""
        keys = set()
        for key in self.cns1_data:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.JSON_OBJS), keys ^ CNS1Constant.JSON_OBJS)

    def test_basic_vars(self):
        """Verify all required 'basic' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["basic"]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.BASIC))

    def test_planned_contin(self):
        """Verify all required 'plannedContingency' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["plannedContingency"]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.PLANNED_CONTIN_KEYS), keys ^ CNS1Constant.PLANNED_CONTIN_KEYS)

    def test_cns1_test_type(self):
        """Verify all required 'cns1TestType' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["cns1TestType"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.CNS1_TEST_TYPE), keys ^ CNS1Constant.CNS1_TEST_TYPE)

    def test_contin_cause(self):
        """Verify all required 'contingencyCause' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["contingencyCause"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.CONTIN_CAUSE), keys ^ CNS1Constant.CONTIN_CAUSE)

    def test_contin_response(self):
        """Verify all required 'contingencyResponse' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["contingencyResponse"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.CONTIN_RESPONSE), keys ^ CNS1Constant.CONTIN_RESPONSE)

    # def test_contin_loiter_alt(self):
    #     """Verify all required 'contingencyLoiterAlt' variables are present in output file."""
    #     keys = set()
    #     for key in self.cns1_data["contingencyLoiterAlt"][0]:
    #         keys.add(key)
    #    print(keys ^ CNS1Constant.CONTIN_LOITER_ALT)
    #     self.assertFalse(bool(keys ^ CONTIN_LOITER_ALT))
    #
    # def test_contin_loiter_type(self):
    #     """Verify all required 'contingencyLoiterType' variables are present in output file."""
    #     keys = set()
    #     for key in self.cns1_data["contingencyLoiterType"][0]:
    #         keys.add(key)
    #    print(keys ^ CNS1Constant.CONTIN_LOITER_TYPE)
    #     self.assertFalse(bool(keys ^ CONTIN_LOITER_TYPE))
    #
    # def test_contin_loiter_rad(self):
    #     """Verify all required 'contingencyLoiterRadius' variables are present in output file."""
    #     keys = set()
    #     for key in self.cns1_data["contingencyLoiterRadius"][0]:
    #         keys.add(key)
    #    print(keys ^ CNS1Constant.CONTIN_LOITER_RAD)
    #     self.assertFalse(bool(keys ^ CONTIN_LOITER_RAD))

    def test_contingency_landing(self):
        """Verify all required 'contingencyLanding' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["contingencyLanding"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.CONTIN_LANDING), keys ^ CNS1Constant.CONTIN_LANDING)

    def test_man_cmd(self):
        """Verify all required 'maneuverCommand' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["maneuverCommand"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.MAN_CMD), keys ^ CNS1Constant.MAN_CMD)

    def test_man_cmd_sent(self):
        """Verify all required 'timeManeuverCommandSent' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["timeManeuverCommandSent"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.TIME_MAN_CMD_SENT), keys ^ CNS1Constant.TIME_MAN_CMD_SENT)

    def test_est_time_man(self):
        """Verify all required 'estimatedTimeToVerifyManeuver' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["estimatedTimeToVerifyManeuver"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.EST_TIME_MAN), keys ^ CNS1Constant.EST_TIME_MAN)

    def test_time_man_cmd_verify(self):
        """Verify all required 'timeManeuverVerification' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["timeManeuverVerification"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.TIME_MAN_CMD_VERIFY), keys ^ CNS1Constant.TIME_MAN_CMD_VERIFY)

    def test_prim_link(self):
        """Verify all required 'primaryLinkDescription' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["primaryLinkDescription"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.PRIM_LINK), keys ^ CNS1Constant.PRIM_LINK)

    def test_redun_link(self):
        """Verify all required 'redundantLinkDescription' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["redundantLinkDescription"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.REDUN_LINK), keys ^ CNS1Constant.REDUN_LINK)

    def test_time_prim_link_discon(self):
        """Verify all required 'timePrimaryLinkDisconnect' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["timePrimaryLinkDisconnect"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.TIME_PRIM_LINK_DISCON), keys ^ CNS1Constant.TIME_PRIM_LINK_DISCON)

    def test_time_redun_link_switch(self):
        """Verify all required 'timeRedundantLinkSwitch' variables are present in output file."""
        keys = set()
        for key in self.cns1_data["timeRedundantLinkSwitch"][0]:
            keys.add(key)
        self.assertFalse(bool(keys ^ CNS1Constant.TIME_REDUN_LINK_SWITCH), keys ^ CNS1Constant.TIME_REDUN_LINK_SWITCH)
