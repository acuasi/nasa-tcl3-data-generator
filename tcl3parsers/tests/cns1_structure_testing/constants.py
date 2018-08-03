"""Declares constants used in CNS1 testing"""

# This is set in runner.py
OUTFILE_NAME = ""

# reusable match cases
ts_match_case = {
    'match': {
        'type': 'str',
        'pattern': r"""^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$"""
    }
}
ts_object_only_match_case = {
    'match': {
        'type': 'list',
        'children': {
            'match': {
                'type': 'dict',
                'children': {
                    'ts': ts_match_case
                }
            }
        }
    }
}

# JSON testing structure, matching what's on swaggerhub
CNS1_MOP = {
    'fType': {
        'match': {
            'exact': 'CNS1'
        }
    },
    'UTM-TCL3-DMP-RevF-CNSPDF': {
        'match': {
            'type': 'str',
            'pattern': r"""^UTM-[^-]+-CNS-[0-9]+.pdf$"""
        }
    },
    'basic': {
        'uvin': {
            'match': {
                'type': 'str',
                'pattern': r"""^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$""",
                'minLength': 36,
                'maxLength': 36
            }
        },
        'gufi': {
            'match': {
                'type': 'str',
                'pattern': r"""^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$""",
                'minLength': 36,
                'maxLength': 36
            }
        },
        'submitTime': {
            'match': {
                'type': 'str',
                'pattern': r"""^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$""",
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
                'pattern': r"""^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$""",
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
                    'match': {
                        'children': {
                            'lat': {
                                'match': {
                                    'type': 'float|int',
                                    'minimum': -90,
                                    'maximum': 90
                                }
                            },
                            'lon': {
                                'match': {
                                    'type': 'float|int',
                                    'minimum': -180,
                                    'maximum': 180
                                }
                            }
                        }
                    }
                }
            }
        },
        'plannedContingencyLandingPointAlt_ft': {
            'match': {
                'exception': None,
                'type': 'list',
                'minLength': 1,
                'children': {
                    'match': {
                        'type': 'int|float|NoneType'
                    }
                }
            }
        },
        'plannedContingencyLoiterAlt_ft': {
            'match': {
                'exception': None,
                'type': 'list',
                'minLength': 1,
                'children': {
                    'match': {
                        'type': 'int|float|NoneType'
                    }
                }
            }
        },
        'plannedContingencyLoiterRadius_ft': {
            'match': {
                'exception': None,
                'type': 'list',
                'minLength': 0,
                'children': {
                    'match': {
                        'type': 'int|float|NoneType'
                    }
                }
            }
        }
    },
    'primaryLinkDescription': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'type': 'dict|NoneType',
                    'children': {
                        'ts': ts_match_case,
                        'primaryLinkDescription': {
                            'match': {
                                'type': 'str',
                                'maxLength': 280
                            }
                        }
                    }
                }
            }
        }
    },
    'redundantLinkDescription': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'type': 'dict|NoneType',
                    'children': {
                        'ts': ts_match_case,
                        'redundantLinkDescription': {
                            'match': {
                                'type': 'str',
                                'maxLength': 280
                            }
                        }
                    }
                }
            }
        }
    },
    'contingencyCause': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'children': {
                        'ts': ts_match_case,
                        'contingencyCause_nonDim': {
                            'match': {
                                'type': 'list',
                                'minLength': 1,
                                'children': {
                                    'match': {
                                        'minimum': 0,
                                        'maximum': 13
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    'contingencyResponse': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'children': {
                        'ts': ts_match_case,
                        'contingencyResponse_nonDim': {
                            'match': {
                                'type': 'int',
                                'minimum': 0,
                                'maximum': 3
                            }
                        }
                    }
                }
            }
        }
    },
    'contingencyLanding': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'children': {
                        'ts': ts_match_case,
                        'contingencyLandingPoint_deg': {
                            'match': {
                                'type': 'list',
                                'minLength': 1,
                                'children': {
                                    'match': {
                                        'type': 'dict',
                                        'children': {
                                            'lat': {
                                                'match': {
                                                    'type': 'int|float',
                                                    'minimum': -90,
                                                    'maximum': 90
                                                }
                                            },
                                            'lon': {
                                                'match': {
                                                    'type': 'int|float',
                                                    'minimum': -180,
                                                    'maximum': 180
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        'contingencyLandingPointAlt_ft': {
                            'match': {
                                'type': 'list',
                                'minLength': 1,
                                'children': {
                                    'match': {
                                        'type': 'float|int'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    },
    'contingencyLoiterType': {
        'match': {
            'exception': None,
            'type': 'list',
            'children': {
                'match': {
                    'children': {
                        'ts': ts_match_case,
                        'contingencyLoiterType_nonDim': {
                            'match': {
                                'type': 'int',
                                'minimum': 0,
                                'maximum': 3
                            }
                        }
                    }
                }
            }
        }
    },
    'contingencyLoiterAlt': {
        'match': {
            'exception': None,
            'type': 'list',
            'children': {
                'match': {
                    'type': 'dict|NoneType',
                    'children': {
                        'ts': ts_match_case,
                        'contingencyLoiterAlt_ft': {
                            'match': {
                                'type': 'list',
                                'minLength': 1,
                                'children': {
                                    'match': {
                                        'type': 'float|int'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    'contingencyLoiterRadius': {
        'match': {
            'exception': None,
            'type': 'list',
            'children': {
                'match': {
                    'type': 'dict|NoneType',
                    'children': {
                        'ts': ts_match_case,
                        'contingencyLoiterRadius_ft': {
                            'match': {
                                'type': 'list',
                                'minLength': 1,
                                'children': {
                                    'match': {
                                        'type': 'float|int',
                                        'minimum': 0
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    'maneuverCommand': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'type': 'dict',
                    'children': {
                        'ts': ts_match_case,
                        'maneuverCommand': {
                            'match': {
                                'type': 'str',
                                'maxLength': 280
                            }
                        }
                    }
                }
            }
        }
    },
    'estimatedTimeToVerifyManeuver': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'type': 'dict',
                    'children': {
                        'ts': ts_match_case,
                        'estimatedTimeToVerifyManeuver_sec': {
                            'match': {
                                'type': 'int|float'
                            }
                        }
                    }
                }
            }
        }
    },
    'cns1TestType': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'type': 'dict',
                    'children': {
                        'ts': ts_match_case,
                        'cns1TestType_nonDim': {
                            'match': {
                                'type': 'int',
                                'minimum': 0,
                                'maximum': 2
                            }
                        }
                    }
                }
            }
        }
    },
    'timeManeuverCommandSent': ts_object_only_match_case,
    'timeManeuverVerification': ts_object_only_match_case,
    'timePrimaryLinkDisconnect': ts_object_only_match_case,
    'timeRedundantLinkSwitch': ts_object_only_match_case
}
