"""Declares constants used in CNS2 testing"""

# This is set in runner.py
OUTFILE_NAME = ""

CNS2_MOP = {
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
                type: 'str'
            }
        },
        'ussInstanceId': {
            'match': {
                'type': 'str',
                'pattern': """^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$""",
                'maxLength': 36,
                'minLength': 36
            }
        }
    }
}
