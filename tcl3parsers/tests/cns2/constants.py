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
            'exact': 'UTM-ACUASI-CNS-2.pdf'
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
    'uasTruth': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'children': {
                        'ts': {
                            'match': {
                                'type': 'str',
                                'pattern': """^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$"""
                            }
                        },
                        'uasTruthEcefXCoordinate_ft': {
                            'match': {
                                'type': 'float'
                            }
                        },
                        'uasTruthEcefYCoordinate_ft': {
                            'match': {
                                'type': 'float'
                            }
                        },
                        'uasTruthEcefZCoordinate_ft': {
                            'match': {
                                'type': 'float'
                            }
                        },
                        'estimatedTruthPositionError95Prct_in': {
                            'match': {
                                'type': 'float|int'
                            }
                        }
                    }
                }
            }
        }
    },
    'prnGpsSat': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'type': 'dict|NoneType',
                    'children': {
                        'ts': {
                            'match': {
                                'type': 'str',
                                'pattern': """^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$"""
                            }
                        },
                        'prnGpsSat_nonDim': {
                            'match': {
                                'type': 'list',
                                'minLength': 1,
                                'children': {
                                    'match': {
                                        'type': 'int',
                                        'minimum': 0,
                                        'maximum': 32
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    'uere': {
        'match': {
            'type': 'list',
            'children': {
                'match': {
                    'children': {
                        'ts': {
                            'match': {
                                'type': 'str',
                                'pattern': """^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$"""
                            }
                        },
                        'uere_in': {
                            'match': {
                                'type': 'float|int'
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
                        'ts': {
                            'match': {
                                'type': 'str',
                                'pattern': """^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$"""
                            }
                        },
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
                        'ts': {
                            'match': {
                                'type': 'str',
                                'pattern': """^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$"""
                            }
                        },
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
                        'ts': {
                            'match': {
                                'type': 'str',
                                'pattern': """^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$"""
                            }
                        },
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
            'type': 'list',
            'children': {
                'match': {
                    'children': {
                        'ts': {
                            'match': {
                                'type': 'str',
                                'pattern': """^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$"""
                            }
                        },
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
            'type': 'list',
            'children': {
                'match': {
                    'type': 'dict|NoneType',
                    'children': {
                        'ts': {
                            'match': {
                                'type': 'str',
                                'pattern': """^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$"""
                            }
                        },
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
            'type': 'list',
            'children': {
                'match': {
                    'type': 'dict|NoneType',
                    'children': {
                        'ts': {
                            'match': {
                                'type': 'str',
                                'pattern': """^2[0-9][0-9][0-9]-[01][0-9]-[0123][0-9]T[012][0-9]:[012345][0-9]:[012345][0-9]\.[0-9][0-9][0-9][0-9]*Z{0,1}$"""
                            }
                        },
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
    }
}
