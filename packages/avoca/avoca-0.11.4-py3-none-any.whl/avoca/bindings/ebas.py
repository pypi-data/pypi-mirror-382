"""Module to handle data of the format required by ebas."""

from __future__ import annotations

import datetime
import logging
import re
from datetime import datetime, timedelta
from enum import IntEnum
from os import PathLike
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from ebas.io.file.nasa_ames import EbasNasaAmes
from nilutility.datatypes import DataObject
from nilutility.datetime_helper import DatetimeInterval

from avoca.bindings.ebas_flags import ebas_flag_to_avoca, flags_to_ebas, nan_flags
from avoca.flags import QA_Flag

logger = logging.getLogger(__name__)


ebas_compname_of_var = {
    "rt": "retention_time",
    "w": "peak_width",
    "area": "peak_area",
}
ebas_compname_to_var = {v: k for k, v in ebas_compname_of_var.items()}


# Additional variables that can be in the dataset (not compound dependant)
additional_vars = [
    "temperature",
    "pressure",
]

titles = {
    "temperature": "T_inlet",
    "pressure": "P_inlet",
}


class DataLevel(IntEnum):
    """Values for different type of data used by ebas."""

    AREAS = 0
    CONCS = 1
    QA_CONCS = 2


concs_data_levels = [DataLevel.CONCS, DataLevel.QA_CONCS]


def data_level_after_qa(data_level: DataLevel) -> DataLevel:
    """Return the data level after the QA."""
    if data_level == DataLevel.CONCS:
        return DataLevel.QA_CONCS
    return data_level


def set_dataframe(
    nas,
    df_export: pd.DataFrame,
    compounds: dict[str, str],
    data_level: DataLevel,
    start_offset: timedelta | None = None,
    end_offset: timedelta | None = None,
    flag_all: list[int] = [],
    invalidate_conc_calib: bool = True,
):
    """Put the data from the export dataframe into the nas object.

    :arg nas: The nas object to fill
    :arg df_export: The dataframe with the data to export. Format follows the
        other avoca format.
    :arg compounds: The dictionary with the compounds. The keys are the
        the names in df_export. Values are the names in ebas.
    :arg data_level: The level of the data to export.
    :arg start_offset: The offset to add to the start time
    :arg end_offset: The offset to add to the end time
    :arg flag_all: List of flags to add to all the data
    :arg invalidate_conc_calib: If True, the concentration calibration
        will be invalidated (flag 980) for all calib samples.
    :returns: A dictionary with the metadata of the compounds exported.
    """

    if ("-", "start_datetime") not in df_export.columns:
        if start_offset is None:
            raise ValueError(
                "start_offset is required if start_datetime is not in df_export"
            )
        df_export[("-", "start_datetime")] = df_export.index + start_offset
    if ("-", "end_datetime") not in df_export.columns:
        if end_offset is None:
            raise ValueError(
                "end_offset is required if end_datetime is not in df_export"
            )
        df_export[("-", "end_datetime")] = df_export.index + end_offset

    nas.sample_times = [
        DatetimeInterval(start, end)
        for start, end in zip(
            df_export[("-", "start_datetime")],
            df_export[("-", "end_datetime")],
        )
    ]

    vars_to_export = {
        DataLevel.AREAS: ["area", "rt", "w", "conc_calib"],
        DataLevel.CONCS: ["C"],
        DataLevel.QA_CONCS: ["C"],
    }

    unit_of_var = {
        "C": "pmol/mol",
        "conc_calib": "pmol/mol",
        "rt": "s",
        "w": "s",
        "area": "area_unit",
        "temperature": "K",
        "pressure": "hPa",
    }

    ebas_varname_of_var = {
        "rt": "rt",
        "w": "pw",
        "area": "pa",
        "conc_calib": "cal",
    }

    dict_flags_to_ebas = flags_to_ebas.copy()

    metadatas = {}

    # Export calibration status if given by the user
    status_col = ("-", "status")
    empty_flags = [[]] * len(df_export)
    if (status_col in df_export.columns) and (data_level not in concs_data_levels):
        metadata = DataObject()
        metadata.comp_name = "status"
        metadata.title = "status"
        metadata.matrix = "instrument"
        metadata.unit = "no unit"
        values = [val for val in df_export[status_col]]
        nas.variables.append(
            DataObject(
                values_=values, flags=empty_flags, flagcol=True, metadata=metadata
            )
        )

    for var in additional_vars:
        var_col = ("-", var)
        if var_col not in df_export.columns:
            continue
        metadata = DataObject()
        metadata.comp_name = var
        metadata.title = titles.get(var, var)
        metadata.matrix = "instrument"
        metadata.unit = unit_of_var[var]
        metadata.cal_scale = ""
        values = [val for val in df_export[var_col]]
        nas.variables.append(
            DataObject(
                values_=values,
                flags=empty_flags,
                flagcol=True,
                metadata=metadata,
            )
        )

    
    this_nan_flags = nan_flags.copy()

    if data_level in concs_data_levels and invalidate_conc_calib:
        # Set the flag to the invalid value instead of the valid calibration
        this_nan_flags.append(QA_Flag.CALIBRATION)
        dict_flags_to_ebas[QA_Flag.CALIBRATION] = 980

    for sub in compounds:
        flag_col = df_export[(sub, "flag")]
        flags = [
            sorted(
                flag_all
                + [dict_flags_to_ebas[f] for f in QA_Flag if f in QA_Flag(flag)]
            )
            for flag in flag_col
        ]
        nan_flag = np.logical_or.reduce([flag_col & flag.value for flag in this_nan_flags])

        for var in vars_to_export[data_level]:
            ebas_name = compounds[sub]
            serie_to_export = df_export[(sub, var)]

            values = [
                None if pd.isna(val) or isnan or (not np.isfinite(val)) else float(val)
                for val, isnan in zip(serie_to_export, nan_flag)
            ]

            metadata = DataObject()
            metadata.comp_name = (
                f"{ebas_name}_{ebas_compname_of_var[var]}"
                if var in ebas_compname_of_var
                else ebas_name
            )
            metadata.title = (
                f"{ebas_name}_{ebas_varname_of_var[var]}"
                if var in ebas_varname_of_var
                else ebas_name
            )
            metadata.unit = unit_of_var[var]
            metadata.matrix = "air"
            # add the variable
            nas.variables.append(
                DataObject(values_=values, flags=flags, flagcol=True, metadata=metadata)
            )

            if var == "conc_calib":
                # Set Nominal/measured=Calibration gas concentration
                vnum = len(nas.variables) - 1
                nas.add_var_characteristics(
                    vnum, "Nominal/measured", "Calibration gas concentration"
                )

            metadatas[sub] = metadata
    return metadatas


def get_last_written_nas_file(directory: Path) -> Path | None:
    """Return path to the last nas file."""

    # Find the last submited files the format is:
    last_file = None
    last_submision_time = None
    for file in directory.glob(f"*.nas"):
        try:
            time_str = file.name.split(".")[2]
            time = datetime.strptime(time_str, "%Y%m%d%H%M%S")
            if last_submision_time is None or time > last_submision_time:
                last_submision_time = time
                last_file = file
        except Exception as e:
            logger.warning(f"Could not parse time from {file}: {e}")

    return last_file


def get_data_level(nas: EbasNasaAmes) -> DataLevel:
    """Get the data level of the nas file."""
    data_level: str = nas.metadata["datalevel"]

    # See https://git.nilu.no/ebas-data-processing/gigas-processing-software/-/issues/1
    if data_level == "1":
        return DataLevel.CONCS
    elif data_level == "1b":
        return DataLevel.QA_CONCS
    elif data_level.startswith("0"):
        return DataLevel.AREAS
    else:
        raise ValueError(f"Data level {data_level} not recognized")


def nas_to_avoca(nas: EbasNasaAmes) -> pd.DataFrame:
    """Convert the ebas file to a pandas dataframe for @voc@.

    To read the nas file, you can do:

    .. code-block:: python

        from ebas.io.file.nasa_ames import EbasNasaAmes

        file = "path/to/file.nas"
        nas = EbasNasaAmes()
        nas.read(file)
        df = nas_to_avoca(nas)


    Doing this will remove some specific flag information.
    In particular, @voc@ only accepts flags per compound and not per variable as in ebas.

    This for each compound, the flag collects all the compounds of the variables.

    @voc@ also requires a runtype for each run.
    We use for that the calibration flag suggested by ebas.
    We have to assume that this flag is the same for all compounds.
    """

    logger = logging.getLogger(__name__)
    clean_for_df = {}

    compounds = []

    for var in nas.variables:
        if "metadata" not in var:
            continue

        metadata = var["metadata"]
        logger.debug(f"Reading variable {metadata}")

        values = var["values_"]

        if "comp_name" not in metadata:
            continue

        comp_name = metadata["comp_name"]

        # Special variable used for calibration
        if comp_name == "status":
            calib_ids = np.array(values, dtype=float)
            mask_nan = np.isnan(calib_ids)
            calib_ids[mask_nan] = 0
            clean_for_df[("-", "status")] = calib_ids.astype(int)
            continue

        if comp_name in additional_vars:
            clean_for_df[("-", comp_name)] = np.array(values, dtype=float)
            continue

        # Split the title on the _
        comp_name = comp_name.split("_")
        if len(comp_name) == 1:
            # Can be either concentration measured or calibration
            compund = comp_name[0]
            title: str = metadata["title"]
            if title.endswith("_cal"):
                variable = "cal"
            else:
                variable = "C"
        elif len(comp_name) == 2:
            compund, variable = comp_name
        elif len(comp_name) == 3:
            compund, var_first, var_second = comp_name
            variable = f"{var_first}_{var_second}"
        elif len(comp_name) == 4 and comp_name[-1] == "compounds":
            # Concentration of merged compounds
            compund = "_".join(comp_name)
            variable = "C"
        else:
            logger.warning(f"passing {comp_name}, could not be understood. Skipping.")
            continue

        if compund not in compounds:
            compounds.append(compund)

        # Convert the variable name to the avoca format
        if variable == "cal":
            # Handled differnetly
            variable = "conc_calib"
        elif variable != "C":
            if variable not in ebas_compname_to_var:
                raise ValueError(f"Variable {variable} not recognized")
            variable = ebas_compname_to_var[variable]

        clean_for_df[(compund, variable)] = np.array(values, dtype=float)

        flag_serie = pd.Series(
            [
                sum([ebas_flag_to_avoca[f].value for f in flag_row])
                for flag_row in var["flags"]
            ],
            dtype=int,
        )
        flag_col = (compund, "flag")
        if variable == "conc_calib":
            # Calibration will have missing values for air smaples
            # so we need to remove the missing values
            flag_serie = int(0)

        if flag_col not in clean_for_df:
            clean_for_df[flag_col] = flag_serie
        else:
            clean_for_df[flag_col] |= flag_serie

    # Use the start of the intervals as the datetime (use 1 for the end)
    clean_for_df[("-", "datetime")] = [dt[0] for dt in nas.sample_times]
    clean_for_df[("-", "start_datetime")] = clean_for_df[("-", "datetime")]
    clean_for_df[("-", "end_datetime")] = [dt[1] for dt in nas.sample_times]

    df = pd.DataFrame(clean_for_df)
    # Runtype, by default assume air samples
    df[("-", "type")] = "air"

    for calib_type, flag in {
        "std": QA_Flag.CALIBRATION,
        "blank": QA_Flag.BLANK,
    }.items():
        is_calib = {
            compound: (flag.value & clean_for_df[(compound, "flag")]).astype(bool)
            for compound in compounds
        }

        # Assert all the calibration flags are the same
        ref_calib = is_calib[compounds[0]]
        for compound in compounds[1:]:
            mask_same = is_calib[compounds[0]] == is_calib[compound]
            if not np.all(mask_same):
                # Show the rows where not all have the same flag
                mask_different = ~mask_same
                logger.warning(
                    f"Calibration flags for {flag} are not the same for all compounds:"
                    f" {compound} is different from reference compound"
                    f" {compounds[0]} at rows {np.argwhere(mask_different).reshape(-1)}"
                )
                # Combine the calib in both samples
                ref_calib = ref_calib | is_calib[compound]
        # Check that we are not overriding another flag
        if not np.all(df.loc[ref_calib, ("-", "type")] == "air"):
            other_types = np.unique(df.loc[ref_calib, ("-", "type")].to_numpy())
            raise ValueError(
                f"Calibration flag {flag} is overriding some {other_types} runs."
            )
        df.loc[ref_calib, ("-", "type")] = calib_type

    return df


def read_ebas_csv(file: PathLike) -> pd.DataFrame:
    """Read the EBAS csv file and return a DataFrame.

    This format comes from other EBAS tools.
    """

    # Check if file is a dir or a file
    kwargs: dict[str, Any] = {"parse_dates": ["Start", "End"], "sep": ";"}
    file = Path(file)
    if file.is_dir():
        # Read all the csv files in the directory
        dfs: list[pd.DataFrame] = [pd.read_csv(f, **kwargs) for f in file.glob("*.csv")]
        df = pd.concat(dfs, axis="index")
    else:
        # Read the csv file
        df = pd.read_csv(file, **kwargs)

    # Read all the columns which are not time
    columns = [c for c in df.columns if c not in ["Start", "End"]]
    # Get the compounds names
    compounds = set(["-".join(c.split("-")[:-1]) for c in columns])
    # Check that for each compounds we have the 4 required parameters
    parameters = ["Value", "Precision", "Accuracy", "Flag"]
    expected_columns = [f"{c}-{p}" for c in compounds for p in parameters]
    missing_columns = [c for c in expected_columns if c not in columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")
    # Make it a multiindex dataframe
    # Get the values for each compound
    df_out = pd.DataFrame(
        columns=pd.MultiIndex.from_product([compounds, ["C", "flag"]])
    )
    flags = {
        0.999: QA_Flag.MISSING.value,
        0.559: QA_Flag.EXTREME_VALUE.value,
        0.147: QA_Flag.BELOW_DETECTION_LIMIT.value,
        0.000: 0,  # Valid
    }
    for c in compounds:
        df_out[(c, "C")] = df[f"{c}-Value"]
        df_out[(c, "flag")] = int(0)
        # Assigne the flag
        df_out[(c, "flag")] |= df[f"{c}-Flag"].apply(lambda x: flags[x])
        # Set values to nan when flagged missing
        # df_out.loc[(df_out[(c, 'flag')] & (QA_Flag.MISSING.value | QA_Flag.BELOW_DETECTION_LIMIT.value)) != 0, (c, 'C')] = np.nan
        df_out.loc[df_out[(c, "flag")] != 0, (c, "C")] = np.nan

    df_out[("-", "type")] = "air"
    df_out[("-", "datetime")] = df["Start"]
    df_out[("-", "datetime_start")] = df["Start"]
    df_out[("-", "datetime_end")] = df["End"]

    return df_out


def extract_concentration_field(text: str) -> dict[str, float]:
    """Extract the concentrations from the text.

    This is a temporary solution that we found to communicate the concentrations
    of the standards thgrough the nas files.
    """
    # Check that the string starts and end with {}
    if not text.startswith("{") or not text.endswith("}") or "{" in text[1:]:
        raise ValueError(
            f"Invalid concentration field: {text}. Must start and end with '{' and '}'"
        )

    text = text[1:-1]  # Remove the brackets

    # Split the substring by comma to separate individual concentrations
    concentration_list = text.split(",")
    # Initialize an empty dictionary to store concentrations
    concentrations = {}
    for concentration in concentration_list:
        # Split each concentration by '=' to separate compound and value
        compound, value = concentration.split("=")
        # Remove leading and trailing whitespaces
        compound = compound.strip()
        value = float(value.strip())  # Convert value to float
        concentrations[compound] = value
    return concentrations


def read_calibrations(nas) -> dict[int, dict[str, str | dict[str, float]]]:
    calibration_str = nas.metadata["cal_std_id"]
    if calibration_str is None:
        logger.warning("No calibration string found from field `cal_std_id`")
        return {}
    if "sec_std_id" in nas.metadata and nas.metadata["sec_std_id"] is not None:
        calibration_str_2 = nas.metadata["sec_std_id"]
        calibration_str += ";" + calibration_str_2
    calib_dict = {}

    calibrations = calibration_str.split(";")
    for calibration in calibrations:
        calibration_id = re.search(
            r"Status calibration standard: (\d+)", calibration
        ).group(1)
        calib_fields = re.split(r",(?![^{}]*\})", calibration, 0)

        fields_dict: dict[str, str | dict[str, float]] = {}
        for field in calib_fields:
            field_parts = field.strip().split(":")
            field_name = field_parts[0].strip()
            fields_dict[field_name] = ":".join(field_parts[1:]).strip()

        calibration_id = int(calibration_id)
        # Check if we have a concentration field
        if "Concentrations" in fields_dict:
            concentration_dict = extract_concentration_field(
                fields_dict["Concentrations"]
            )
            fields_dict["Concentrations"] = concentration_dict

        calib_dict[calibration_id] = fields_dict

    return calib_dict
