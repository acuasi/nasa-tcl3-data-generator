"""Testing suite runner file for cns2"""
import unittest

import constants
import cns1

import value_tests
import variable_tests

class Runner():
    """Executes parser and runs the testing suite"""
    def __init__(self):
        """Loads all tests"""
        tests = unittest.TestSuite()
        loader = unittest.TestLoader()
        tests.addTests(loader.loadTestsFromModule(value_tests))
        tests.addTests(loader.loadTestsFromModule(variable_tests))
        self.suite = tests

    def __runParser(self):
        """Runs parser"""
        cns1.generate(constants.MI_FILE_NAME,
                      constants.DF_FILE_NAME,
                      constants.FIELD_VARS_NAME,
                      constants.OUTFILE_NAME)

    def run(self):
        """Runs testing suite"""
        self.__runParser()
        runner = unittest.TextTestRunner(verbosity=3)
        return runner.run(self.suite)

if __name__ == '__main__':
    testRunner = Runner()
    test = testRunner.run()
    print ("TSET")
