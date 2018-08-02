"""Defines the structure for CNS2 with default values"""
data = {
    "fType": "CNS2",
    "UTM-TCL3-DMP-RevF-CNSPDF": "UTM-ACUASI-CNS-2.pdf",
    "basic": {
        "uvin": None,
        "gufi": None,
        "submitTime": None,
        "ussInstanceID": None,
        "ussName": None
    },
    "plannedContingency": {
        "plannedContingencyLandingPoint_deg": None,
        "plannedContingencyLandingPointAlt_ft": 0,
        "plannedContingencyLoiterAlt_ft": [0],
        "plannedContingencyLoiterRadius_ft": [0]
    },
    "prnGPSSat": [
        {
            "ts": None,
            "prnGpsSat_nonDim": None
        }
    ],
    "uere": [
        {
            "ts": None,
            "uere_in": None
        }
    ],
    "contingencyCause": [
        None
    ],
    "contingencyResponse": [
        None
    ],
    "contingencyLoiterType": [
        None
    ],
    "contingencyLoiterAlt": [
        {
            "ts": None,
            "contingencyLoiterAlt_ft": [0]
        }
    ],
    "contingencyLoiterRadius": [
        {
            "ts": None,
            "contingencyLoiterRadius_ft": [0]
        }
    ],
    "contingencyLanding": [
        None
    ],
    "uasTruth": [
        None
    ]
}
