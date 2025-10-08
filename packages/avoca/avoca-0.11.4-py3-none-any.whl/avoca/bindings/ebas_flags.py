# https://projects.nilu.no/ccc/flags/flags.html for more info on what ebas uses
from avoca.flags import QA_Flag

flags_to_ebas: dict[QA_Flag, int] = {
    QA_Flag.MISSING: 999,  # 	M 	Missing measurement, unspecified reason
    QA_Flag.ZERO_NEG_CONC_EXT: 999,
    QA_Flag.INVALIDATED_EXT: 900,  # 	H 	Hidden and invalidated by data originator
    # V Extremely high value, outside four times standard deviation in a lognormal distribution
    QA_Flag.EXTREME_VALUE: 458,
    QA_Flag.CALIBRATION: 683,  # 	I 	Invalid due to calibration. Used for Level 0.
    QA_Flag.BLANK: 684,  #  	Invalid due to zero/span check. Used for Level 0.
    QA_Flag.HEIGHT_INTEGRATION: 0,  # 	Valid
    QA_Flag.UNCORRELATED: 0,  # 	Valid
    QA_Flag.MET_OFFICE_BASELINE: 0,  # 	Valid
    QA_Flag.BELOW_DETECTION_LIMIT: 147,  # 	B 	Below detection limit
    QA_Flag.POLLUTION: 900,
    QA_Flag.SUSPICIOUS_RT: 900,
    QA_Flag.INVALID_VALUES: 999,  # 	M 	Missing measurement, unspecified reason
}

ebas_flag_to_avoca: dict[int, QA_Flag] = {
    ebas_flag: avoca_flag for avoca_flag, ebas_flag in flags_to_ebas.items()
}
# Set some flags with Multiple values to the same value
ebas_flag_to_avoca.pop(0)  # 0 is valid in avoca
ebas_flag_to_avoca[999] = QA_Flag.MISSING
ebas_flag_to_avoca[900] = QA_Flag.INVALIDATED_EXT
# Unspecified contamination or local influence, but considered valid
ebas_flag_to_avoca[559] = QA_Flag.POLLUTION
ebas_flag_to_avoca[685] = (
    QA_Flag.CALIBRATION
)  #  	Invalid due to secondary standard gas measurement. Used for Level 0.
ebas_flag_to_avoca[980] = (
    QA_Flag.CALIBRATION
)  # Missing due to calibration or zero/span check

missing_flags = set(QA_Flag) - set(flags_to_ebas.keys())
if missing_flags:
    raise RuntimeError(
        f"Not all QA flags are mapped to Ebas flags. Missing: {missing_flags}"
    )

# Flags that are considered to have missing values
nan_flags = [
    QA_Flag.MISSING,
    QA_Flag.ZERO_NEG_CONC_EXT,
    QA_Flag.INVALIDATED_EXT,
    QA_Flag.INVALID_VALUES,
]

# priority of the flag to appear in the output
# Useful when you can select only one flag value
flag_order = [
    QA_Flag.CALIBRATION,
    QA_Flag.BLANK,
    QA_Flag.HEIGHT_INTEGRATION,
    QA_Flag.MET_OFFICE_BASELINE,
    QA_Flag.BELOW_DETECTION_LIMIT,
    QA_Flag.POLLUTION,
    QA_Flag.SUSPICIOUS_RT,
    QA_Flag.UNCORRELATED,
    QA_Flag.EXTREME_VALUE,
    QA_Flag.INVALIDATED_EXT,
    QA_Flag.ZERO_NEG_CONC_EXT,
    QA_Flag.MISSING,
    QA_Flag.INVALID_VALUES,
]
