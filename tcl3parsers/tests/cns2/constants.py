"""Declares constants used in CNS2 testing"""

# This is set in runner.py
OUTFILE_NAME = ""

CNS2_MOP = {
    'fType': {
        'match': {
            'exact': 'CNS2'
        }
    },
    'UTM-TCL3-DMP-RevF-CNSPDF': {
        'match': {
            'exact': 'UTM-SAMPLE-CNS-4.pdf'
        }
    },
    'basic': {
        'uvin': {
            'match': {
                'type': 'str',
                'pattern': """^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$""",
                'minLength': 36,
                'maxLength': 36
            }
        },
        'gufi': {
            'match': {
                'type': 'str',
                'pattern': """^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$""",
                'minLength': 36,
                'maxLength': 36
            }
        },
        'submitTime': {
            'match': {
                'type': 'str',
                'pattern': """^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$""",
            }
        },
        'ussName': {
            'match': {
                'type': 'str'
            }
        },
        'ussInstanceID': {
            'match': {
                'type': 'str',
                'pattern': """^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$""",
                'maxLength': 36,
                'minLength': 36
            }
        }
    },
    'plannedContingency': {
        'plannedContingencyLandingPoint_deg': {
            'match': {
                'type': 'list',
                'minLength': 1,
                'children': {
                    'lat': {
                        'match': {
                            'type': 'int',
                            'minimum': -90,
                            'maximum': 90
                        }
                    },
                    'lon': {
                        'match': {
                            'type': 'int',
                            'minimum': -180,
                            'maximum': 180
                        }
                    }
                }
            }
        },
        'plannedContingencyLandingPointAlt_ft': {
            'match': {
                'type': 'list',
                'minLength': 1,
                'children': {
                    'match': {
                        'type': 'int'
                    }
                }
            }
        },
        'plannedContingencyLoiterAlt_ft': {
            'match': {
                'type': 'list',
                'minLength': 1,
                'children': {
                    'match': {
                        'type': 'int'
                    }
                }
            }
        },
        'plannedContingencyLoiterRadius_ft': {
            'match': {
                'type': 'list',
                'minLength': 0,
                'children': {
                    'match': {
                        'type': 'int'
                    }
                }
            }
        }
    },
}
# TODO: Add JSON structure for uasTruth and below
