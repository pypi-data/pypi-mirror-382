"""Flag for the qa tool.

.. note:: The documentation for the flags is generated from the code by reading
    the comments written in this file.
"""

from enum import Flag, auto


class QA_Flag(Flag):
    """Enum for QA flags."""

    # Missing value
    MISSING = auto()
    # A value of 0 or negative was calculated by an external software, but the value is marked as valid
    ZERO_NEG_CONC_EXT = auto()
    # invalidated before the qa tool
    INVALIDATED_EXT = auto()

    # Extreme value detected
    EXTREME_VALUE = auto()
    # Uncorrelated expected compounds
    # The compounds is expected to be correlated with another one, but it is not
    UNCORRELATED = auto()

    # Calibration run
    CALIBRATION = auto()
    # Blank run
    BLANK = auto()

    # Height integration instead of area integration
    HEIGHT_INTEGRATION = auto()

    # Pollution flag
    POLLUTION = auto()

    # Baseline
    MET_OFFICE_BASELINE = auto()

    # Below detection limit
    BELOW_DETECTION_LIMIT = auto()

    # Bad retention time values
    SUSPICIOUS_RT = auto()

    # Invalid Values
    INVALID_VALUES = auto()


if __name__ == "__main__":
    # Print the flages and their values
    for flag in QA_Flag:
        print(f"{flag.name} = {flag.value}")
