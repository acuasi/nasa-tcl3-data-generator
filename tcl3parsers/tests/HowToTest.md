# NOTICE
While this structure is still used, it is now encapsulated in an entirely automated generation and testing suite. This can be found in `tcl3parsers/tests/generic`. Documentation for this is available [here](../PARSER.md).
# Testing the parsers
In order to make testing easier, a controller was created for generically testing the structure of any JSON. This controller matches outputted JSON files from the parser directly against every specification for the variables.
## Creating Structure Tests
In order to setup structure testing, start by creating a new directory for the parser's testing. Under this directory, there are three important files to make, `constants.py`, `runner.py`, `structure_tests.py`. The naming conventions of the file don't matter as long as they internally reference each other correctly.

### structure_tests.py
This is the main entry file used to extend the StructureTestController class and add testing functions for the Python unittest framework. To start, the StructureTestController and constants need to be imported. Then, a new class needs to be declared to extend the StructureTestController. An example class would look like below:
```py
class StructureTests(StructureTestController.StructureTestController):
    @classmethod
    def setUpClass(cls):
        generatedFile = open(constants.OUTFILE_NAME, "r")
        cls.cns1_data = json.load(generatedFile)

    def test_structure(self):
        self.runStructureTest(constants.CNS1_MOP, self.cns1_data)
```
As can be seen in the example above, the setUpClass is used to load the JSON file initially and the test_structure class is used to actually run the tests. The reason for the above being implemented as a class extension though comes down to the Python unittest framework. Any function starting with `test_` is treated as a test case. So in the example above, only one test case will be run that will handle all testing. However, the above could also be written to have a test function for each top level master variable. Both ways would produce the same results, but the difference would be that Python unittest would show more printout for the latter. If there is any other specific testing that needs to be done outside of allowed constraints for the test file, these could also be added here.

### runner.py
As the name implies, this file is used to actually run the parsers and testing suite. This file can be set up to run for a single flight, or for all flights in a folder. In addition to this, all unittests are loaded in this file. So if there is additional testing needed beyond the structure tests, the files can be added here and these unit tests will be automatically run. The crux of this file is the Runner class, an example of this file can be found [here](cns1/runner.py).

### constants.py
`constants.py` is the testing JSON file used by the Structure Test Controller. In this file, the testing JSON structure should be defined according to the specification. The following are the allowed constraints:
- `exception`
    - Used to short circuit further testing if the outputted value matches
- `exact`
    - Will only pass if the outputted value is exactly the same
- `type`
    - The desired type of the object (types are python based)
- `pattern`
    - A regular expression that the value must match
- `minLength`
    - The minimum length of the outputted value. This can refer to string length, list length, or any other container based length.
- `maxLength`
    - The maximum length of the outputted value. Like minLength, this works for taking the length of any object with the length property.
- `maximum`
    - The maximum numeric value that the outputted value can be.
- `minimum`
    - The minimum numeric value that the outputted value can be.
- `children`
    - This keyword is used as a way to tell the test controller in order to match constraints against all children of a variable. For example, if a variable held a list, then the children constraint paired with the another constraint such as type could be used to make sure all children were of that type.

In order to minimize variable name conflicts with certain keywords, the above keywords will only be checked for if they are directly nested under the `match` keyword. If a keyword is not nested under the `match` keyword, then it will just be treated as a normal variable.

#### Example constants file
```json
EXAMPLE_MOP = {
    "int_variable_less_than_100": {
        "match": {
            "type": "int",
            "maximum": 100
        }
    },
    "list_of_int_variables_greater_than_0": {
        "match": {
            "type": "list",
            "children": {
                "match": {
                    "type": "int",
                    "minimum": 0
                }
            }
        }
    },
    "list_of_lat_lon_coordinates": {
        "match": {
            "type": "list",
            "children": {
                "match": {
                    "type": "dict",
                    "children": {
                        "lat": {
                            "match": {
                                "type": "float|int",
                                "minimum": -90,
                                "maximum": 90
                            }
                        },
                        "lon": {
                            "match": {
                                "type": "float|int",
                                "minimum": -180,
                                "maximum": 180
                            }
                        }
                    }
                }
            }
        }
    }
}
```
##### Example Explanation
- int_variable_less_than_100
    - The variable must be of type int
    - The variable must be less than 100
- list_of_int_variables_greater_than_0
    - The variable must be a list
    - All children of this variable must:
        - Be of type int
        - Be greater than 0
- list_of_lat_lon_coordinates
    - This variable must be a list
    - All children of this variable must be a dictionary
        - All dictionary children must:
            - Have the key `lat` that must:
                - Be of type float or int
                - Have a minimum of -90
                - Have a maxmimum of 90
            - Have the key `lon` that must:
                - Be of type float or int
                - Have a minimum of -180
                - Have a maxmimum of 180
